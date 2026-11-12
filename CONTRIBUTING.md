# Contribuir a FolioScan

Los cambios al código propio se distribuyen bajo la misma licencia PolyForm Noncommercial 1.0.0. Conserva los avisos de autoría y las licencias de terceros. No incorpores código sin derechos suficientes ni documentos personales a las pruebas.

1. Lee README y docs/ARQUITECTURA.md.
2. Instala las dependencias indicadas en docs/COMPILACION.md.
3. Haz cambios pequeños, con comentarios sobre decisiones y límites. Hay una explicación adicional de cada línea en docs/CODIGO_COMENTADO.html.
4. Ejecuta las pruebas de la plataforma afectada. Para cambios destructivos, comprueba también cancelación, fallo de escritura y recuperación.
5. Describe comportamiento anterior, comportamiento nuevo y comprobaciones realizadas.

## Traducciones

`shared/translations.tsv` es el catálogo canónico UTF-8. La primera columna contiene la cadena española usada como clave; las siguientes corresponden a los once idiomas. No cambies claves existentes sin actualizar sus usos. Se admite `\n` para saltos de línea. Ejecuta `python scripts/sync_translations.py` después de editarlo. Las traducciones nuevas deben completar todas las columnas y probarse con textos largos.

Para proponer otro idioma, contacta con [Brass-Ebort](https://github.com/Brass-Ebort). Añadirlo requiere actualizar también CODES/NAMES de ambos clientes.
