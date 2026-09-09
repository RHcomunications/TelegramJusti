\# TelegramJusti 1.3.0

Complemento híbrido de accesibilidad compatible con Telegram Desktop y Unigram Preview 12.10.3.0.



TelegramJusti amplía la accesibilidad de Telegram mediante atajos de teclado, automatización accesible y navegación optimizada para usuarios de NVDA.



\## Características



\* Grabación y envío de mensajes de voz.

\* Cancelación de grabación de mensajes de voz.

\* Reproducción y pausa de audios.

\* Llamadas y videollamadas.

\* Acceso rápido a perfiles.

\* Adjuntar archivos multimedia.

\* Creación rápida de nuevos chats.

\* Acceso rápido al cuadro de edición de mensajes.

\* Volver directamente a la lista de chats.

\* Apertura del menú de navegación.

\* Enfoque automático en la lista de chats.

\* Compatibilidad híbrida con Telegram Desktop y Unigram.

\* Gestos reasignables desde Gestos de Entrada de NVDA.



\## Compatibilidad



\* NVDA 2026.1 o posterior.

\* Compatible con NVDA 2026.1.1.

\* Arquitectura x64.

\* Telegram Desktop.

\* Unigram.



\## Novedades de la versión 1.3.0

* Compatibilidad con Unigram Preview 12.10.3.0.
* Actualización de AutomationIDs: se añadieron IDs alternativos para cada control.
* `ComposerHeaderCancel` como fallback para cancelación de grabación.
* `RecognizedText` como fallback para detección de mensajes de voz.
* Búsqueda multi-IDs para todos los botones principales.
* Se añadieron nombres alternativos para botón finalizar (End, Leave).
* Se añadieron nombres alternativos para reproducción (Play, Pause).
* Nuevo script de diagnóstico Ctrl+Shift+D para registrar jerarquía de elementos.
* Mejora en la detección de perfil y navegación mediante listas de IDs compatibles.
* Se mejoró la robustez de todas las búsquedas de UI Automation.

### Nuevas funcionalidades

* **Mensajes**: Editar (Retroceso), responder (Enter), reenviar (Alt+F), eliminar (Alt+Delete / Shift+Delete).
* **Navegación rápida**: Alt+1 a Alt+6 para lista de chats, último mensaje, no leídos, carpetas, perfil, hilos.
* **Audio**: Velocidad de reproducción (Alt+S), cerrar reproductor (Alt+E), convertir voz a texto (NVDA+Alt+R).
* **Ventana emergente**: Mostrar texto (Alt+C), abrir comentarios (Ctrl+Alt+C), copiar mensaje (Ctrl+C).
* **Rebobinado**: Rebobinar/reavanzar voz (Ctrl+Alt+←/→).
* **Búsqueda**: Ir a resultados (Alt+I), siguiente/anterior (F3/Shift+F3).
* **Llamadas**: Aceptar (Alt+Y), rechazar/terminar (Alt+N), silenciar (Alt+A), cámara (Alt+V).
* **Configuración**: Diálogo de ajustes NVDA (NVDA+Alt+U), configuración persistente.
* **Soporte**: 17 idiomas, efectos de sonido, TextWindow, GlobalPlugin.
* **Accesibilidad completa**: Menú contextual integrado, procesamiento dinámico de elementos.

\## Novedades de la versión 1.2.0

* Añadida función para cancelar grabación de mensajes de voz mediante Ctrl+Shift+R.
* Añadida función para volver directamente a la lista de chats mediante Alt+Flecha izquierda.
* Implementado enfoque automático en la lista de chats al iniciar Unigram.
* Migración al sistema moderno de scripts mediante `@script`.
* Eliminación del sistema heredado `__gestures`.
* Los gestos ahora son reasignables desde Gestos de Entrada de NVDA.
* Migración progresiva a UI Automation y AutomationID.
* Mejora significativa de compatibilidad multilenguaje.
* Optimización de la detección de mensajes de voz mediante AutomationID `Recognize`.
* Mejoras generales de estabilidad y mantenimiento del código.



\## Autor



\*\*Mauro Ocampo - JustiCode\*\*



\## Repositorio



https://github.com/JustiCode/TelegramJusti



\## Agradecimientos



A mi familia, por acompañar y sostener la atemporalidad de mi labor como incipiente y obstinado desarrollador de software accesible.


A los compañeros que oficiaron como Beta Testers realizando pruebas en distintos equipos, arquitecturas de Telegram y sistemas operativos, además de aportar ideas y sugerencias que enriquecieron el proyecto.


Un agradecimiento especial a Héctor Benítez de NVDA.ES por su paciencia, humildad y buena onda al recibir la presentación del complemento, brindandome sugerencias, recomendaciones y hasta una herramienta para su publicación.



Asimismo, mi agradecimiento a José Manuel Delicado por sus comentarios y aportes técnicos, fundamentales durante el proceso de migración de scripts, modernización mediante `@script`, eliminación del sistema heredado de gestos y sustitución progresiva de llamadas basadas en etiquetas localizadas por AutomationID, contribuyendo a un complemento más robusto, estable y multilingüe.

## Seguridad

TelegramJusti sigue las políticas de seguridad de NVDA para prevenir inyección de código y otras vulnerabilidades:

* Sin uso de `eval()`, `exec()`, o `compile()` sobre datos de usuario.
* Validación de longitud en nombres de objetos (máximo 2000 caracteres).
* Configuración validada mediante `ConfigObj` con esquema estricto.
* Todos los `except` usan `except Exception:` (no bare `except:`).
* Sin deserialización de datos no confiables.
* Dependencias empaquetadas y API pública de NVDA utilizada exclusivamente.

Véase [SECURITY.md](SECURITY.md) para más detalles.

## Licencia

TelegramJusti se distribuye bajo la licencia GNU General Public License v2 (GPL v2) o posterior.

## Copyright

Copyright © 2026 Mauro Ocampo - JustiCode.

## Historial de versiones

- **1.0.0** — Primera versión pública del complemento.

- **1.2.0** — Nuevas funciones de navegación y gestión de mensajes de voz, migración a AutomationID, modernización mediante `@script` y gestos reasignables desde gestos de entrada de NVDA.

- **1.3.0** — Compatibilidad con Unigram Preview 12.10.3.0. Actualización de AutomationIDs con múltiples fallbacks, nuevo script de diagnóstico y mejora de robustez en todas las búsquedas de UI Automation.

Finalmente, gracias a toda la comunidad de NVDA  y Justicia Ciega, cuya experiencia compartida hace posible seguir construyendo herramientas para todos y todas.



