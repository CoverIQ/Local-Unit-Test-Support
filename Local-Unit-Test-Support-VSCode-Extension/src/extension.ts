// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import simpleGit, { SimpleGit } from 'simple-git';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "CoverIQ-Local-Unit-Test-Support" is now active!');

	// Register the main command for the extension. This command is defined in package.json.
	let disposable = vscode.commands.registerCommand('CoverIQ-Local-Unit-Test-Support.analyze', async () => {
        // Get the currently opened folder in VS Code. This is our target repository.
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('Please open a workspace folder first.');
            return;
        }
        const workspacePath = workspaceFolders[0].uri.fsPath;

        // Retrieve the path to the Python executable from the virtual environment.
        const config = vscode.workspace.getConfiguration('coveriq');
        const pythonExecutablePath = config.get<string>('pythonPath');
        if (!pythonExecutablePath) {
            vscode.window.showErrorMessage('Python executable path for CoverIQ is not set. Please configure it in the settings.');
            return;
        }

        // Define constants for the analysis process.
        const outputFileName = 'report'; // Or make this configurable
        const pythonScriptPath = path.join(context.extensionPath, 'Local-Unit-Test-Support', 'main.py');
        const outputPath = path.join(workspacePath, `${outputFileName}.md`);
        let fromCommit: string | undefined;
        let toCommit: string | undefined;

        try {
            // Initialize simple-git in the workspace directory.
            const git: SimpleGit = simpleGit(workspacePath);
            
            // Verify that the opened folder is a valid Git repository.
            if (!(await git.checkIsRepo())) {
                vscode.window.showErrorMessage('The current folder is not a Git repository.');
                return;
            }

            // Fetch the commit history, including "decorations" like branch and tag names.
            const log = await git.log(['--decorate=full']);

            if (!log.all.length) {
                vscode.window.showErrorMessage('No commits found in this repository.');
                return;
            }

            // Format the raw commit log into a user-friendly format for the QuickPick UI.
            const commitItems = log.all.map(commit => {
                const branchInfo = commit.refs ? `  [${commit.refs}]` : '';
                return {
                    label: commit.message,
                    description: `${commit.hash.substring(0, 7)}${branchInfo}`,
                    detail: `${commit.author_name} on ${new Date(commit.date).toLocaleString()}`,
                    hash: commit.hash
                };
            });

            // Prompt the user to select the "from" (older) commit.
            const fromPick = await vscode.window.showQuickPick(commitItems, {
                placeHolder: 'Select the FROM commit (the older one)',
                title: 'Select Start Commit'
            });
            
            // Exit if the user cancels the selection (e.g., by pressing ESC).
            if (!fromPick) {
                vscode.window.showInformationMessage('Analysis cancelled.');
                return;
            }
            fromCommit = fromPick.hash;

            // Prompt the user to select the "to" (newer) commit.
            const toPick = await vscode.window.showQuickPick(commitItems, {
                placeHolder: 'Select the TO commit (the newer one, press Enter for HEAD)',
                title: 'Select End Commit'
            });
            
            if (!toPick) {
                vscode.window.showInformationMessage('Analysis cancelled.');
                return;
            }
            toCommit = toPick.hash;

        } catch (error: any) {
            console.error('Failed to read git log:', error);
            vscode.window.showErrorMessage(`Failed to read Git history: ${error.message}`);
            return;
        }

        // Assemble the full command to execute the Python script with all arguments.
        let command = `${pythonExecutablePath} ${pythonScriptPath} --repo-path "${workspacePath}" --output ${outputFileName}`;
        if (fromCommit) {
            command += ` --from ${fromCommit}`;
        }
        if (toCommit) {
            command += ` --to ${toCommit}`;
        }

        // Use the withProgress API to show a cancellable notification to the user.
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing Unit Tests...",
            cancellable: true
        }, async (progress, token) => {
            token.onCancellationRequested(() => {
                // You might need a way to kill the child process here
                vscode.window.showWarningMessage("Analysis cancelled.");
            });

            progress.report({ increment: 0 });

            return new Promise<void>((resolve, reject) => {
                // Execute the command as a child process.
                exec(command, { cwd: workspacePath }, (error, stdout, stderr) => {
                    progress.report({ increment: 100 });
                    if (error) {
                        vscode.window.showErrorMessage(`Error: ${error.message}`);
                        reject();
                        return;
                    }
                    if (stderr) {
                        vscode.window.showWarningMessage(`Stderr: ${stderr}`);
                    }
                    if (stdout) {
                        console.log(`Stdout from Python script: ${stdout}`);
                    }

                    // Show the generated report
                    const reportUri = vscode.Uri.file(outputPath);
                    vscode.commands.executeCommand('markdown.showPreview', reportUri);
                    resolve();
                });
            });
        });
    });

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
