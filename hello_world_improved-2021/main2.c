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

    srand(time(0));
    bool flag = true;
    char current = 0;
    char *reference = "hello, world";
    int length = strlen(reference);
    char output[length];

    for (int i=0; i<length; i++)
    {
        if (reference[i] > 'z' || reference[i] < 'a')
            output[i] = reference[i];
        
        while(output[i] != reference[i])
        {
            usleep(sleepTime);
            
            output[i] = 97 + rand() % 26;
            for (int j=0; j<i+1; j++)
                printf("%c", output[j]);
            printf("\n");            
        }
    }
}