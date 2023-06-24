#include <stdio.h>
#include <string.h>

#define LIMIT 128
#define STR_VALUE(x) STR(x)
#define STR(x) #x


int main(int argc, char *argv[])
{
	char str[LIMIT+1] = {0};
	FILE *fp;
	int exit;

	if (argc < 2)
	{
		fputs("ERROR syntax: get_exit_code <file>\n", stderr);
		return(1);
	}

	fp = fopen(argv[1], "r");
	if (fp == NULL)
	{
		fputs("ERROR: Could not open file\n", stderr);
		return(1);
	}

	while (!feof(fp))
	{
		if (fscanf(fp, "%" STR_VALUE(LIMIT) "s", str) != 1)
		{
			fputs("ERROR: exit code not found\n", stderr);
			return(1);
		} 

		if (!strcmp(str, "EXIT_CODE"))
		{
			if (fscanf(fp, "%d", &exit) != 1)
			{
				fputs("ERROR: exit code not found\n", stderr);
				return(1);
			} 
			printf("%d\n", exit);
			return 0;
		}
	}
	fputs("ERROR: exit code not found\n", stderr);
	return(1);
}