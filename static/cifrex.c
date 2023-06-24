/*
 * cifrex.c
 * Authors:	Pedro Arroz Serra &
 * 		Hugo Castro
 * Date: 25/04/2020
 */

#include <stdio.h>
/*#include <string.h>*/
#include <ctype.h>

#define NCHARS 36
#define TMAX 50
#define TMIN 2
#define SMAX 35
#define SMIN -35
#define TXTSZ 166
#define DIM (2*TXTSZ)


const char chars[NCHARS] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'};


char * encript_trans (char *str, int n);
char * reverse(char *, const unsigned int);
char * encrypt(char *, const unsigned int);
char * rot(char *, int, unsigned int);
char * decrypt(char *, const unsigned int, int);
char * bill_r(char *);
char * bill_l(char *, unsigned int);

char * bill(char *, int, unsigned int);



long unsigned int str_len(const char *s)
{
	int i = 0;
	for (; *(s+i) != 0 ; i++)
		;
	return i;
}


char * str_cpy(char *dest, const char * src)
{
	int i = 0;
	for ( ; src[i] != 0 ; i++)
		dest[i] = src[i];
	dest[i] = 0;

	return dest;
}





int main(void)
{
	char op, texto[2*TXTSZ+2] = ""; /* enough space for eventually necessary padding */
	char input[DIM];
	int n=0, col=0, len=0;

	while (1) {
		fgets(input, DIM, stdin);
		if (sscanf(input, " %c", &op) < 1)
			continue;

		if (op == 'q')
		{
			printf("Exiting->\n");
			return 0;
		}

		switch(op)
		{
		case 's' :
			if (sscanf(input, " %c %d %[^\n]",&op, &n,texto) != 3)
				continue;
			if (n < SMIN || n > SMAX)
			{
				printf("Error: out of bound\n");
				continue;
			}
			puts(rot(texto, n, str_len(texto)));

			break;
		case 'S' :
			if (sscanf(input, " %c %d %[^\n]",&op, &n,texto) != 3)
				continue;
			if (n < SMIN || n > SMAX)
			{
				printf("Error: out of bound\n");
				continue;
			}
			puts(rot(texto, -n, str_len(texto)));
			break;
		case 't' :
			if (sscanf(input, " %c %d %[^\n]",&op, &n,texto) != 3)
				continue;
			if (n < TMIN || n > TMAX)
			{
				printf("Error: out of bound\n");
				continue;
			}
			puts(encript_trans(texto,n));

			break;
		case 'T' :
			if (sscanf(input, " %c %d %[^\n]",&op, &n,texto) != 3)
				continue;
			if (n < TMIN || n > TMAX)
			{
				printf("Error: out of bound\n");
				continue;
			}
    		len = str_len(texto);
			col = len % n == 0 ? len / n : len/n + 1;
			puts(encript_trans(texto,col));
			break;


		case 'e':
			if (sscanf(input, " %c %[^\n]",&op, texto) != 2)
				continue;

			puts(encrypt(texto, str_len(texto)));
			break;

		case 'E':
			if (sscanf(input, " %c %[^\n]",&op, texto) != 2)
				continue;

			puts(decrypt(texto, str_len(texto), 0));
			break;

		case 'r':
			if (sscanf(input, " %c %d %[^\n]",&op, &n, texto) != 3)
				continue;

			puts(bill(texto, n, str_len(texto)));
			break;

		case 'h':
			puts(texto);
			break;

		default:
			printf("Error: Unknown option\n");
		}
	}
}



char * reverse(char *s, const unsigned int n)
{
	char t;
	unsigned int i;
	for (i = 0 ; i < n/2 && s[i] != '\0'; i++)
	{
		t = s[n-1-i];
		s[n-1-i] = s[i];
		s[i] = t;
	}
	return s;
}

char * encrypt(char *s, const unsigned int length)
{
	int k = length / 2;
	int n = length - k;

	if (length <= 2)
		return s;

	encrypt(reverse(s, k), k);
	encrypt(reverse(s+k, n), n);
	return s;
}

char * decrypt(char *s, const unsigned int length, int it)
{
	int k, n;
	if (length <= 2)
		return s;

	k = length / 2;
	if (it % 2 && length % 2)
		k++;

	n = length - k;

	decrypt(reverse(s, k), k, it+1);
	decrypt(reverse(s+k, n), n, it+1);
	return s;
}

char * rot(char * s, int n, unsigned int length)
{
	char c;
	int h;
	unsigned int i;
	char *ptr = NULL;
	
	printf("ola");
	putchar(2);
	putchar(3);
	
	fflush(stdout);
	
	for (i = *ptr; s[i] != '\0' && i < length; i++)
	{
		c = toupper(s[i]);
		if (isdigit(c))
		{
			if (n >= 0)
				h = (c - '0' + n) % NCHARS;
			else
				h = (c - '0' + n) >= 0 ?  c - '0' + n : NCHARS + n + c - '0';

			s[i] = chars[h];
			continue;
		}
		if (isalpha(c))
		{
			if (n >= 0)
				h = (10 + c - 'A' + n) % NCHARS;
			else
				h = (10 + c - 'A' + n) >= 0 ? 10 + c - 'A' + n : NCHARS + n + 10 + c - 'A';
			s[i] = chars[h];
			continue;
		}
	}
	
	return ptr;
}

char * encript_trans (char *str, int cols)
{
	int padding, len, lines, i, l, c, t_lines, t_cols;
	char str_aux[2*TXTSZ+2];

	len = str_len(str);
	padding = cols - len % cols;
	lines = len % cols == 0 ? len / cols : len/cols + 1;

	/* add spaces in the end of str to make len divisible by cols */
	for (i = 0; i < padding; i++)
		str[len+i] = ' ';
	str[len + i] = 0;

	/* copy original str to an auxiliary location */
	str_cpy(str_aux, str);

	/* the transpose will have */
	t_lines = cols;
	t_cols = lines;

	/* create the transpose directly */
	for(c = 0, i = 0; c < t_cols ; c++) /* run through columns */
	{
		for (l = 0 ; l < t_lines ; l++) /* run through lines */
		{

			str[c+l*t_cols] = str_aux[i];
			/*  this is the same as doing:
			array_res[l][c] = str_aux[i]; */
			i++;
		}
	}

	return str;

}


char * bill_r(char * s)
{
	char c, aux;
	unsigned int i = 0;

	for (i = 1, c = s[0] ; s[i] != '\0' ; i++)
	{
		aux = s[i];
		s[i] = c;
		c = aux;
	}
	s[0] = c;

	return s;
}

char * bill_l(char * s, unsigned int len)
{
	char c;
	unsigned int i = 0;

	for (i = 1, c = s[i] ; s[i] != '\0' ; i++)
	{
		s[i] = s[(i+1) % len];
	}
	s[0] = c;

	return s;
}


char * bill(char * s, int n, unsigned int len)
{
	int i;
	int absN = n >= 0 ? n : -n;

	if (len <= 1)
		return s;

	for (i = 0 ; i < absN ; i ++)
	{
		s = n > 0 ? bill_r(s) : bill_l(s, len);
	}

	return s;
}
