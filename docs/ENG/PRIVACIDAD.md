# Privacy and Permissions

FolioScan does not include accounts, advertising, its own telemetry, or a document server. PDF operations, conversions, layout composition, and search run locally.

Android uses the Google Play Services document scanner. Its initial setup may download components through Google Play; Google's terms and operating practices apply. FolioScan's own APK does not request Internet permission. The scanner manages its camera through Google Play Services; file-manager permissions are separate.

To find and manage PDFs on the phone, Android 11 and later request “All files access” to shared storage. Android 8–10 use read/write permissions. Private data belonging to other apps is not accessed. `Android/data` and `Android/obb` are skipped. If you deny access, you can still scan and use the system file pickers. Distribution through Google Play would require a review of its broad file-access policies; this package is intended for direct installation.

Sharing a document grants read access to the selected app. Exporting to a cloud provider using the system file picker may upload the document at the user's request; FolioScan does not control that provider.

Windows uses the webcam with operating-system permission. Photos and PDFs are stored in `Datos` next to the executable or in user-selected destinations. Files are not encrypted: anyone with access to those folders can read them. `.recovery` files contain the previous version of a PDF.

The Android app disables automatic backups of its library. Export your documents before uninstalling. On Windows, retain `Datos` to preserve the session, library, and settings. Also delete copies and recovery files when you want to permanently remove a document.
