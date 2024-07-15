#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <ctype.h>

/*
  Function Declarations for builtin shell commands:
 */
int shell_cd(char **args);
int shell_help(char **args);
int shell_exit(char **args);

/*
  List of builtin commands, followed by their corresponding functions.
 */
char *builtin_str[] = {
  "cd",
  "help",
  "exit"
};

int (*builtin_func[]) (char **) = {
  &shell_cd,
  &shell_help,
  &shell_exit
};

int shell_num_builtins() {
  return sizeof(builtin_str) / sizeof(char *);
}

/*
  Builtin function implementations.
*/

/**
   @brief Builtin command: change directory.
   @param args List of args.  args[0] is "cd".  args[1] is the directory.
   @return Always returns 1, to continue executing.
 */
int shell_cd(char **args)
{
  if (args[1] == NULL) {
    fprintf(stderr, "shell: expected argument to \"cd\"\n");
  } else {
    if (chdir(args[1]) != 0) {
      perror("shell");
    }
  }
  return 1;
}

/**
   @brief Builtin command: print help.
   @param args List of args.  Not examined.
   @return Always returns 1, to continue executing.
 */
int shell_help(char **args)
{
  int i;
  printf("Custom shell made in C\n");
  printf("Type program names and arguments, and hit enter.\n");
  printf("The following are built in:\n");

  for (i = 0; i < shell_num_builtins(); i++) {
    printf("  %s\n", builtin_str[i]);
  }

  printf("Use the man command for information on other programs.\n");
  return 1;
}

/**
   @brief Builtin command: exit.
   @param args List of args.  Not examined.
   @return Always returns 0, to terminate execution.
 */
int shell_exit(char **args)
{
  return 0;
}

/**
  @brief Launch a program and wait for it to terminate.
  @param args Null terminated list of arguments (including program).
  @return Always returns 1, to continue execution.
 */
int shell_launch(char **args)
{
  pid_t pid;
  int status;

  pid = fork();
  if (pid == 0) {
    // Child process
    if (execvp(args[0], args) == -1) {
      perror("shell");
    }
    exit(EXIT_FAILURE);
  } else if (pid < 0) {
    // Error forking
    perror("shell");
  } else {
    // Parent process
    do {
      waitpid(pid, &status, WUNTRACED);
    } while (!WIFEXITED(status) && !WIFSIGNALED(status));
  }

  return 1;
}

/**
   @brief Execute shell built-in or launch program.
   @param args Null terminated list of arguments.
   @return 1 if the shell should continue running, 0 if it should terminate
 */
int shell_execute(char **args)
{
  int i;

  if (args[0] == NULL) {
    // An empty command was entered.
    return 1;
  }

  for (i = 0; i < shell_num_builtins(); i++) {
    if (strcmp(args[0], builtin_str[i]) == 0) {
      return (*builtin_func[i])(args);
    }
  }

  return shell_launch(args);
}

char *shell_read_line(void)
{
  char *line = NULL;
  ssize_t bufsize = 0; // have getline allocate a buffer for us

  if (getline(&line, &bufsize, stdin) == -1){
    if (feof(stdin)) {
      exit(EXIT_SUCCESS);  // We recieved an EOF
    } else  {
      perror("readline");
      exit(EXIT_FAILURE);
    }
  }

  return line;
}

char **shell_split_line(char *line)
{
  int count = 0;
  int capacity = 10;
  char **argv = malloc(capacity * sizeof(char *));
  const char *p = line;
  char *current_arg = NULL;
  int current_length = 0;
  int in_quotes = 0;

  while (*p)
  {
    if (isspace(*p) && !in_quotes)
    {
      if (current_length > 0)
      {
        current_arg[current_length] = '\0';
        argv[count++] = current_arg;
        current_length = 0;
        current_arg = NULL;
        if (count >= capacity)
        {
          capacity *= 2;
          argv = realloc(argv, capacity * sizeof(char *));
        }
      }
    }
    else
    {
      if (!current_arg)
      {
        current_arg = malloc(strlen(p) + 1);
      }
      if (*p == '"')
      {
        in_quotes = !in_quotes;
      }
      else if (*p == '\\' && (*(p + 1) == '"' || *(p + 1) == '\\'))
      {
        p++;
        current_arg[current_length++] = *p;
      }
      else
      {
        current_arg[current_length++] = *p;
      }
    }
    p++;
  }

  if (current_length > 0)
  {
    current_arg[current_length] = '\0';
    argv[count++] = current_arg;
  }

  argv[count] = NULL;

  // *argc = count;
  return argv;
}

void shell_loop() {
  char *line;
  char **args;
  int status;

  do {
    char cwd[256];
    getcwd(cwd, sizeof(cwd));
    printf("%s -shell> ", cwd);
    line = shell_read_line();
    // int argc;
    args = shell_split_line(line);
    status = shell_execute(args);

    free(line);
    free(args);
  } while (status);
}

int main(int argc, char **argv) {
  // Load configuration files, if any.

  // Run command loop.
  shell_loop();

  // Perform any shutdown/cleanup.

  return EXIT_SUCCESS;
}