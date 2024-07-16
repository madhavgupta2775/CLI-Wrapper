#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <ctype.h>

#define BUFFER_SIZE 1024

void execute_command(const char *command, char *output) {
    int pipefd[2];
    pid_t pid;
    int status;
    
    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }
    
    pid = fork();
    if (pid == 0) {
        // Child process
        close(pipefd[0]); // Close unused read end
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        char *args[] = {"/bin/sh", "-c", (char *)command, NULL};
        if (execvp(args[0], args) == -1) {
            perror("shell");
        }
        exit(EXIT_FAILURE);
    } else if (pid < 0) {
        // Error forking
        perror("shell");
    } else {
        // Parent process
        close(pipefd[1]); // Close unused write end
        waitpid(pid, &status, 0);

        // Read command output
        ssize_t nbytes;
        while ((nbytes = read(pipefd[0], output, BUFFER_SIZE)) > 0) {
            output += nbytes;
        }
        close(pipefd[0]);
    }
}
