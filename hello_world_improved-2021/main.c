#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char *argv[])
{  
    if (argc != 2)
    {
        printf("Useage: ./name <sleep-time-in-ms>\n");
        return 1;
    }
    int sleepTime = atoi(argv[1]);
    if (sleepTime > 10000)
        sleepTime = 10000;

    srand(time(0));
    bool flag = true;
    char current = 0;
    char *reference = "hello world";
    int length = strlen(reference);
    char output[length];


    while (flag)
    {
        for (int j=0; j<length; j++)
        {
            usleep(sleepTime);

            if(reference[j] == output[j])
                printf("%c", output[j]);
            else if (reference[j] > 'z' || reference[j] < 'a')
            {
                output[j] = reference[j];
                printf("%c\n", output[j]);
                break;
            }
            else
            {
                output[j] = 97 + rand() % 26;
                printf("%c\n", output[j]);
                break;
            }

            if (j == length-1)
            {
                flag = false;
                printf("\n");
            }

        }
    }
    return 0;
}