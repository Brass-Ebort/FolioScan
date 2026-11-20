# Privacy and permissions

FolioScan has no accounts, advertisements, its own telemetry or a document server. PDF operations, conversion, composition and file discovery run locally.

Android uses Google ML Kit Document Scanner through Google Play Services. Components and updates may be downloaded by that external service. According to Google's terms, document inputs and results are processed on-device and are not sent to Google servers for processing. ML Kit can send performance and usage metrics to Google. FolioScan's lack of the INTERNET permission does not prevent Google Play Services communications. Do not describe the application as sending absolutely no data outside the phone.

Official information: https://developers.google.com/ml-kit/terms and https://developers.google.com/ml-kit/android-data-disclosure . The Google scanner handles camera access through Play Services; document-management permissions are separate.

Since 0.4.0, normal search uses only Documents/FolioScan and its subfolders via the Android folder picker. Grant access once to Documents (or directly FolioScan); the persisted grant is used only to search FolioScan. Normal mode does not need broad device access. Settings offers an optional whole-device mode after a warning: Android 11+ requests all-files access; Android 8–10 requests storage read/write access. Search is bounded and cancellable. Disabling the mode stops using broad access; revoke the OS permission separately in system settings if desired. Other applications' private data cannot be accessed; Android/data and Android/obb are skipped. Google Play publication requires a separate policy review; this distribution is for direct installation.

Sharing grants read access to the application chosen by the user. Selecting a cloud provider as the export destination may upload the document by the user's choice; FolioScan does not control that provider.

Windows uses the webcam subject to system permission. Pictures and PDFs are stored in Datos next to the executable or in selected output folders. FolioScan adds no at-rest encryption: anyone with filesystem access may read them. .recovery files contain the previous PDF version.

Android automatic backup of the private library is disabled. Export before uninstalling. On Windows, keep Datos to preserve settings, library and sessions. Delete exported copies and recovery copies as well when intentionally removing a document permanently.
