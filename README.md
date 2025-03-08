# 🍪​ NewGalleto-M

<br>
<img src="static/Logo.png" alt="Imagen de unas nubes">

<br>

## Explicación del uso del repositorio:

El repositorio tiene **Son 7 ramas** para un mejor control de trabajo

### Ramas princpales
1. **main:** Donde estara todo el proyecto finalizado. Se modificara cuando ya este en las últimas etapas
2. **develop:** Area de purbeas en conjunto. Aquí es donde integraremos y porbaremos los m´+ódulos antes de fucionarlos con `main`.

### Las de trabajo para cada uno
Cada uno estaremos en dentro de nuestra rama donde crearemos **sub ramas** para cada módulo que desarrollemos.

3. isaac
4. cesarZ
5. cesarM
6. Fabian
7. Andres

---
<br>
<br>
<br>


## Forma de trabajar:

1. CLonar el repositorio con `git clone`:
`git clone https://github.com/isaacrdmc/NewGalleto-M.git`

2. Crear una rama dentro de tú rama para el trabajo con `checkout`:
`git checkout -b tuRama/nombre-modulo`

3. Realiar los `commits` con cada cambio significativo:
`git add .`
`git commit -m " Hola Equipo! "`

4. Actualizar los cambios con la rama `develop` antes hacer `push`
    git checkout develop
    git pull origin develop
    git checkout feature/nombre-modulo
    git merge develop

5. Antes de subir los cambios al repositorio con `push`:
`git push origin feature/nombre-modulo`

--- 
<br>
<br>
<br>


## Base de Datos (MySQL)


* Todos utilizaremos la misma BD dentro de manera local con los mimso nombres de las tablas
* En el scritp de la conexión manejaremos las credenciales a través de variables de entorno para evitar problemas.
* Si despues necesitamos modificar algun campo en la BD notificar al equipo para hacer los cambios necesarios a la BD
--- 

## Estrucutra del poryecto

### static
Es donde estaran todos los archivos que no van a cambian dinámicamente en el proyecto, como los estilos, scripts y archivos multimedia.
Es donde iran las hojas de estilo, los JS y las imágenes como el logo.

### templates
Aca es donde estaran las páginass de HTML y el contenido dinámico para la web.

### módulos
Es donde cada uno debera de crear una carpeta de sú módulo donde se usara para el backend y frontend.

### database
Aquí se almacenan los archivos relacionados con la base de datos.
COmo por ejemplo la conexión.

### app.py 
Es donde se configura la aplicación y se registran los módulos.
