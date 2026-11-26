#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include "transformaciones.h"

#define NUM_THREADS 8

int main(int argc, char *argv[])
{
    if (argc < 4) {
        printf("Uso: %s <kernel_size> <filtros_8bits> <img1.bmp> [img2.bmp ...]\n", argv[0]);
        return 1;
    }

    int kernel_size = atoi(argv[1]);
    char *filtros = argv[2];

    if (strlen(filtros) < 8) {
        printf("Error: La mascara de filtros debe tener 8 bits (ej. 10100000).\n");
        return 1;
    }

    int total_imagenes = argc - 3;
    if (total_imagenes > 10) {
        total_imagenes = 10;
    }

#ifdef _WIN32
    system("if exist resultados rmdir /s /q resultados");
    system("del /q imagen_*.bmp 2>nul");
    system("mkdir resultados");
#else
    system("rm -rf './resultados'");
    system("rm -f imagen_*.bmp");
    system("mkdir -p './resultados'");
#endif

    omp_set_num_threads(NUM_THREADS);
    double inicio = omp_get_wtime();

    printf("Procesando %d imagen(es) con kernel %d...\n\n", total_imagenes, kernel_size);
    fflush(stdout);

    for (int k = 0; k < total_imagenes; k++) {
        char *ruta_imagen = argv[3 + k];
        printf("Procesando [%d/%d]: %s\n", k + 1, total_imagenes, ruta_imagen);
        fflush(stdout);

        char comando_prep[1024];
#ifdef _WIN32
        snprintf(comando_prep, sizeof(comando_prep),
                 "mkdir \"resultados\\Imagen%d\" & copy /Y \"%s\" \"resultados\\Imagen%d\\original.bmp\" >nul",
                 k + 1, ruta_imagen, k + 1);
#else
        snprintf(comando_prep, sizeof(comando_prep),
                 "mkdir -p './resultados/Imagen%d' && cp -f \"%s\" './resultados/Imagen%d/original.bmp'",
                 k + 1, ruta_imagen, k + 1);
#endif
        system(comando_prep);

        #pragma omp parallel
        {
            #pragma omp sections
            {
                #pragma omp section
                if (filtros[0] == '1') inv_hor_color(ruta_imagen);

                #pragma omp section
                if (filtros[1] == '1') inv_hor_bn(ruta_imagen);

                #pragma omp section
                if (filtros[2] == '1') inv_ver_color(ruta_imagen);

                #pragma omp section
                if (filtros[3] == '1') inv_ver_bn(ruta_imagen);

                #pragma omp section
                if (filtros[4] == '1') blur_color(ruta_imagen, kernel_size);

                #pragma omp section
                if (filtros[5] == '1') blur_bn(ruta_imagen, kernel_size);

                #pragma omp section
                if (filtros[6] == '1') bordes_x(ruta_imagen);

                #pragma omp section
                if (filtros[7] == '1') bordes_y(ruta_imagen);
            }
        }

        char comando_mv[2048];
#ifdef _WIN32
        snprintf(comando_mv, sizeof(comando_mv),
            "if exist imagen_horizontal_color.bmp move /Y imagen_horizontal_color.bmp \"resultados\\Imagen%d\\hor_color.bmp\" >nul & "
            "if exist imagen_horizontal_bn.bmp move /Y imagen_horizontal_bn.bmp \"resultados\\Imagen%d\\hor_bn.bmp\" >nul & "
            "if exist imagen_vertical_color.bmp move /Y imagen_vertical_color.bmp \"resultados\\Imagen%d\\ver_color.bmp\" >nul & "
            "if exist imagen_vertical_bn.bmp move /Y imagen_vertical_bn.bmp \"resultados\\Imagen%d\\ver_bn.bmp\" >nul & "
            "if exist imagen_blur_color.bmp move /Y imagen_blur_color.bmp \"resultados\\Imagen%d\\blur_color.bmp\" >nul & "
            "if exist imagen_blur_bn.bmp move /Y imagen_blur_bn.bmp \"resultados\\Imagen%d\\blur_bn.bmp\" >nul & "
            "if exist imagen_bordes_x.bmp move /Y imagen_bordes_x.bmp \"resultados\\Imagen%d\\bordes_x.bmp\" >nul & "
            "if exist imagen_bordes_y.bmp move /Y imagen_bordes_y.bmp \"resultados\\Imagen%d\\bordes_y.bmp\" >nul",
            k + 1, k + 1, k + 1, k + 1, k + 1, k + 1, k + 1, k + 1);
#else
        snprintf(comando_mv, sizeof(comando_mv),
            "mv -f imagen_horizontal_color.bmp './resultados/Imagen%d/hor_color.bmp' 2>/dev/null; "
            "mv -f imagen_horizontal_bn.bmp './resultados/Imagen%d/hor_bn.bmp' 2>/dev/null; "
            "mv -f imagen_vertical_color.bmp './resultados/Imagen%d/ver_color.bmp' 2>/dev/null; "
            "mv -f imagen_vertical_bn.bmp './resultados/Imagen%d/ver_bn.bmp' 2>/dev/null; "
            "mv -f imagen_blur_color.bmp './resultados/Imagen%d/blur_color.bmp' 2>/dev/null; "
            "mv -f imagen_blur_bn.bmp './resultados/Imagen%d/blur_bn.bmp' 2>/dev/null; "
            "mv -f imagen_bordes_x.bmp './resultados/Imagen%d/bordes_x.bmp' 2>/dev/null; "
            "mv -f imagen_bordes_y.bmp './resultados/Imagen%d/bordes_y.bmp' 2>/dev/null",
            k + 1, k + 1, k + 1, k + 1, k + 1, k + 1, k + 1, k + 1);
#endif
        system(comando_mv);
    }

#ifdef _WIN32
    system("del /q imagen_*.bmp 2>nul");
#else
    system("rm -f imagen_*.bmp");
#endif

    double fin = omp_get_wtime();
    double tiempo_total = fin - inicio;

    printf("\nProceso completado.\n");
    printf("Tiempo total de ejecucion: %f segundos\n", tiempo_total);
    fflush(stdout);

    return 0;
}