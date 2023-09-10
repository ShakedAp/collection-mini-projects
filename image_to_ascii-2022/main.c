#include <stdio.h>
#include <string.h>
#include <math.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image_resize.h"

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: ./bin <filename> <scale>\n");
        return 1;
    }
    
    float scale = .1;
    if (argc == 3)
        scale = atof(argv[2]);

    const char *lightAscii = ".,:;ox%#@"; // change light characters as needed. For example add space
    const long int lightAsciiLen = strlen(lightAscii);
    int width, height, channels;
    
    // Load the image from the disk
    unsigned char *img = stbi_load(argv[1], &width, &height, &channels, 0);
    printf("Image dimenstions: %d   px by %dpx.\n", width, height);
    if (img == NULL)
    {
        printf("Could not load \"%s\".\n", argv[1]);
        return 2;
    }

    // Rescale the image
    const int newWidth = round(width*scale), newHeight = round(height*scale);
    printf("New dimenstions: %dpx by %dpx.\n", newWidth, newHeight);
    if(newWidth > 1000 || newHeight > 1000)
    {
        printf("Dimenstions too big!\n");
        return 4;
    }
    unsigned char resized[newWidth*newHeight*channels];
    if(!stbir_resize_uint8(img, width, height, 0, resized, newWidth, newHeight, 0, channels))
    {
        printf("Couldn't resize image.\n");
        return 3;
    }
    
    // Loop through each pixel and print the corresponding light level ASCII char.
    unsigned char *pixels = resized;
    for (int i=0; i<newHeight; i++)
    {
        for(int j=0; j<newWidth; j++)
        {
            int R = *pixels++, G = *pixels++, B = *pixels++;
            if (channels > 3)
                pixels++;
            
            float avg = (R + G + B) / 3.0f;
            int index = floor((avg / 255.0f) * lightAsciiLen);
            putchar(lightAscii[index]);
            putchar(lightAscii[index]);
        }
        putchar('\n');
    }

    stbi_image_free(img);
    return 0;
}