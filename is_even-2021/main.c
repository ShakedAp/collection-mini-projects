#include <stdio.h>
#include <stdlib.h>
#include<unistd.h>

#define LINES 10000


int main(int argc, char **argv)
{
    char * filename = "output.c";

    if(argc > 1)
        filename = argv[1];

    FILE* outFile = fopen(filename, "w");

    if (outFile == NULL)
    {
        printf("An error occured while trying to open the %s\n", filename);
        return -1;
    }

    fprintf(outFile, "#include <stdio.h>\n\n"
            "int main(void)\n"
            "{\n"
            "\tint x;\n"
            "\tprintf(\"Enter a number to be checked: \");\n"
            "\tscanf(\"%%d\", &x);\n"
            "\tprintf(\"The number you entered is %%d\\n\", x);\n\n"
            "\tif(x < 0)\n\t\tx = -x;\n"
            "\tif(x >= %d)\n\t{\n\t\tprintf(\"The number is too big!!\\n\");\n\t\treturn -1;\n\t}\n\n"
            "\tprintf(\"It is \");\n", LINES);      


    printf("Starting to write to %s\n", filename);
    for(int i = 0; i < LINES; i++)
    {
        if(i % (LINES/100) == 0 && i != 0)
            printf("finished %.1f%% of lines so far.\n", (i * 100.0f)/ LINES );
        
        fprintf(outFile, "\tif(x==%d)printf(\"%s\");\n", i, i % 2 ? "odd" : "even");
    }

    fprintf(outFile, "\n\tprintf(\"!\\n\");\n");
    fprintf(outFile, "}");
    fclose(outFile);
    printf("Finished writing to the %s\n", filename);
}