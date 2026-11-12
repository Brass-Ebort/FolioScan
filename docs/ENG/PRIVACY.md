# Privacy and permissions

FolioScan has no accounts, advertisements, its own telemetry or a document server. PDF operations, conversion, composition and file discovery run locally.

Android uses Google ML Kit Document Scanner through Google Play Services. Components and updates may be downloaded by that external service. According to Google's terms, document inputs and results are processed on-device and are not sent to Google servers for processing. ML Kit can send performance and usage metrics to Google. FolioScan's lack of the INTERNET permission does not prevent Google Play Services communications. Do not describe the application as sending absolutely no data outside the phone.

Official information: https://developers.google.com/ml-kit/terms and https://developers.google.com/ml-kit/android-data-disclosure . The Google scanner handles camera access through Play Services; document-management permissions are separate.

Searching shared storage on Android 11 or later requests all-files access. Android 8–10 use storage read/write permissions. Other applications' private data cannot be accessed; Android/data and Android/obb are skipped. Denying broad access does not prevent using the scanner and system file pickers. Google Play publication would require a separate review of its storage-access policies; these APKs are prepared for direct installation.

Sharing grants read access to the application chosen by the user. Selecting a cloud provider as the export destination may upload the document by the user's choice; FolioScan does not control that provider.

Windows uses the webcam subject to system permission. Pictures and PDFs are stored in Datos next to the executable or in selected output folders. FolioScan adds no at-rest encryption: anyone with filesystem access may read them. .recovery files contain the previous PDF version.

Android automatic backup of the private library is disabled. Export before uninstalling. On Windows, keep Datos to preserve settings, library and sessions. Delete exported copies and recovery copies as well when intentionally removing a document permanently.
