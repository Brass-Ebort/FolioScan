# FolioScan 0.4.0 — EXE portable autónomo — 20/11/2026

Windows se entrega como **FolioScan-0.4.0.exe**, un único archivo que se puede copiar y ejecutar sin instalar Python ni Visual C++. El ZIP contiene ese mismo EXE e instrucciones. Las dependencias se extraen a una carpeta temporal privada durante la ejecución. Datos se crea junto al EXE: solo es necesario copiarla si se quieren conservar documentos y preferencias. Bibliotecas es opcional y permite reemplazos LGPL compatibles.

## Corrección de la entrega anterior
La entrega anterior exigía conservar _internal e instalar un runtime externo; no cumplía el objetivo de EXE autónomo. Se ha corregido el empaquetado sin rediseñar la interfaz de Windows. Se ha añadido únicamente la presentación de condiciones Microsoft al primer inicio, con aceptación/cancelación y recuerdo de la decisión junto a los datos portables.

## Procedencia y condiciones
- **libffi 3.4.4 amd64:** copia oficial python/cpython-bin-deps, commit 94cb9a1c7feb608adf2b9f8fe2dbd6925ffbf90d. SHA-256 eff52743773eb550fcc6ce3efc37c85724502233b6b002a35496d828bd7b280a. LICENSE exacto del mismo commit, copyright 1996–2022 Anthony Green, Red Hat, Inc and others. El script verifica los bytes antes de compilar; no se atribuye esa procedencia a la DLL antigua.
- **Microsoft:** se ha encontrado una instalación completa y estable de Visual Studio Community 2026 en el equipo, dato no comprobado en la entrega anterior. Se toman las DLL release de VC/Redist, no de System32 ni de las ruedas Python. Sus diez firmas Authenticode son válidas y se conservan sus bytes; el alias NumPy tiene el mismo contenido. No se incluyen debug_nonredist ni previews. La licencia Community permite el desarrollo individual de aplicaciones propias y redistribuir los componentes listados, con obligaciones. Se archivan los documentos oficiales íntegros y una extracción de texto. El programa aporta funcionalidad principal, conserva avisos, no atribuye respaldo Microsoft y muestra las condiciones de uso del runtime. Los distribuidores deben conservar sus condiciones protectoras, cumplir las restricciones de distribución e indemnidad previstas por la licencia, y no aplicar PolyForm/LGPL al código Microsoft. Quien compile/redistribuya debe disponer de derechos aplicables; la presencia del software no es una certificación jurídica universal. Evidencia: legal/microsoft-runtime-provenance.json.
- **Qt/PySide/Shiboken 6.12.0:** se conservan avisos y textos LGPL/GPL, las fuentes oficiales completas de qtbase, qtsvg, qtimageformats y pyside-setup, y su manifiesto. El paquete de fuentes debe acompañar al EXE en la Release. Se permite expresamente la ingeniería inversa necesaria para depurar modificaciones LGPL. Bibliotecas/PySide6 y Bibliotecas/shiboken6 permiten sustituir componentes compatibles sin recompilar ni comprobar firmas. La prueba modifica únicamente la marca temporal COFF de Qt6Core y verifica los bytes efectivamente cargados; no demuestra compatibilidad de cambios arbitrarios.
- **Seguridad:** pypdf 7.1.0 y setuptools 84.2.1 corrigen los rangos afectados de las once alertas aportadas. legal/dependency-security-check.json registra la consulta de avisos para las versiones fijadas. No es garantía de ausencia de vulnerabilidades desconocidas.

## Verificación y límites
Se han ejecutado 21 pruebas Windows, incluidas las operaciones PDF/imagen, arrastrar/soltar, idiomas y la aceptación/cancelación de condiciones usando texto sintético. La autoprueba del EXE verifica 13 grupos de funciones. Los informes de carga comprueban que libffi, Qt y el CRT Microsoft se cargan desde la extracción integrada, no desde una instalación externa. Se prueba mover únicamente el EXE a otra carpeta y ejecutar con PATH reducido. Se verifican hashes y paquetes de publicación.

No se han probado webcam física ni una máquina Windows limpia sin runtime instalado. No se ha desinstalado ni modificado el runtime del sistema. El EXE no está firmado con Authenticode; las DLL Microsoft originales sí tienen firma válida. Android se recompila como 0.4.0/code 8, con la misma firma de publicación, paquete es.folioscan.app y depuración desactivada. No se ha probado en un teléfono físico ni en un emulador con Servicios de Google Play. No se modifica GitHub ni las versiones históricas. Las capturas privadas permanecen en Registros, fuera de la distribución. El titular debe disponer de derechos sobre el icono aportado.

## Evidencias y fuentes
- legal/libffi-provenance.json, microsoft-runtime-provenance.json, windows-functional-check.json, windows-portable-loader.json, lgpl-replacement-verification.json y windows-binary-inventory.json.
- https://visualstudio.microsoft.com/license-terms/vs2026-ga-community/
- https://visualstudio.microsoft.com/license-terms/vs2026-ga-visualcpp-v14-redist-runtime/
- https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution
- https://www.qt.io/development/open-source-lgpl-obligations
- https://github.com/python/cpython-bin-deps/tree/94cb9a1c7feb608adf2b9f8fe2dbd6925ffbf90d

Las fuentes propias y los scripts de compilación/empaquetado están actualizados en el ZIP de código. Los hashes de entrega se encuentran en SHA256SUMS.txt. La lista de cambios para GitHub está en CAMBIOS_REPOSITORIO.txt.

## Android 0.4.0

Se añade Documentos/FolioScan mediante SAF como ámbito normal. El análisis amplio es opcional y requiere confirmar un aviso. Se conservan las operaciones de renombrar, eliminar y ampliar PDF; el reemplazo SAF guarda previamente una copia Recuperacion-*.pdf. La búsqueda tiene límites, cancelación y descarte de resultados tardíos. El tema inicial sigue el sistema salvo preferencia manual.

Bouncy Castle bcprov/bcpkix/bcutil pasa de 1.72 a 1.87. legal/android-security-before.json conserva los avisos previos; legal/android-security-check.json consulta las 60 coordenadas Maven únicas resueltas. El informe de Windows consulta sus 16 dependencias fijadas. No hay avisos conocidos devueltos en estas consultas; no se ha hecho una auditoría exhaustiva de todo el código de terceros.

Las pruebas Android cubren PDF/imagen, orientación, preferencias, búsqueda acotada/cancelación/tiempo agotado, autorización explícita del modo amplio y un proveedor SAF local simulado (crear carpeta, ámbito, límites, renombrar sin sobrescribir, borrar y ampliar con recuperación). Lint de release no presenta errores; conserva advertencias de estilo/recursos y TrustAllX509TrustManager en bcpkix. FolioScan no usa el cliente TLS de esa biblioteca ni declara INTERNET; esta advertencia no se oculta. El escáner de Google se ejecuta mediante Servicios de Google Play y puede descargar componentes y comunicar métricas técnicas según sus términos.
