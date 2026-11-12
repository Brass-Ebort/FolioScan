# Privacy and Permissions

FolioScan does not include accounts, advertisements, its own telemetry, or a document server. PDFs, conversions, page composition, and searching are processed locally.

Android uses the document scanner provided by Google Play Services. Its initial setup may download components through Google Play; its terms and operation are governed by Google. The application's own APK does not request Internet permission. Google Play handles the scanner's camera access; file-manager permissions are separate.

To find and manage PDFs on the phone, Android 11 and later request “All files access” for shared storage. Android 8–10 use read/write permissions. Private data belonging to other applications is not accessed. `Android/data` and `Android/obb` are excluded. If you deny access, you can still scan documents and use file pickers. Distribution through Google Play would require a review of its broad file-access policies; this package is prepared for direct installation.

Sharing a document grants read permission to the selected application. Exporting to a cloud provider through the system picker may upload it at the user's choice; FolioScan does not control that provider.

Windows uses the webcam with system permission. Photos and PDFs are stored in `Datos` alongside the executable or in the destinations you select. Files are not encrypted: anyone with access to those folders can read them. `.recovery` files contain the previous version of a PDF.

The Android app disables automatic backups of its library. Export documents before uninstalling. On Windows, retain `Datos` to preserve the session, library, and settings. Also delete copies and recovery files when you want to permanently remove a document.
