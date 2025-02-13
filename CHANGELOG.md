## [v2.18.1](https://github.com/DS4SD/docling-core/releases/tag/v2.18.1) - 2025-02-13

### Fix

* Update Pillow constraints ([#157](https://github.com/DS4SD/docling-core/issues/157)) ([`a9afeda`](https://github.com/DS4SD/docling-core/commit/a9afeda6d1251900142571f7bff3d00d871d5915))

## [v2.18.0](https://github.com/DS4SD/docling-core/releases/tag/v2.18.0) - 2025-02-10

### Feature

* Add ContentLayer attribute to designate items to body or furniture ([#148](https://github.com/DS4SD/docling-core/issues/148)) ([`786f0c6`](https://github.com/DS4SD/docling-core/commit/786f0c68336a7b9cced5fb0cb66427b050955e32))

## [v2.17.2](https://github.com/DS4SD/docling-core/releases/tag/v2.17.2) - 2025-02-06

### Fix

* Define LTR/RTL text direction in HTML export ([#152](https://github.com/DS4SD/docling-core/issues/152)) ([`3cf31cb`](https://github.com/DS4SD/docling-core/commit/3cf31cbe384e3f77a375aa057ef61d156d990b23))

## [v2.17.1](https://github.com/DS4SD/docling-core/releases/tag/v2.17.1) - 2025-02-03

### Fix

* Image fallback for malformed equations ([#149](https://github.com/DS4SD/docling-core/issues/149)) ([`eb9b4b3`](https://github.com/DS4SD/docling-core/commit/eb9b4b39a1a2f81baf72d3fa3bbc7cd8ed594c1c))

## [v2.17.0](https://github.com/DS4SD/docling-core/releases/tag/v2.17.0) - 2025-02-03

### Feature

* **HTML:** Fallback showing formulas as images ([#146](https://github.com/DS4SD/docling-core/issues/146)) ([`23477f7`](https://github.com/DS4SD/docling-core/commit/23477f76741b3593734287776fdf5e0761558c2d))
* **HTML:** Export formulas with mathml ([#144](https://github.com/DS4SD/docling-core/issues/144)) ([`ed36437`](https://github.com/DS4SD/docling-core/commit/ed36437346177b9249c98df3eb5ddeadef004c59))

### Fix

* Add html escape in md export and fix formula escapes ([#143](https://github.com/DS4SD/docling-core/issues/143)) ([`c6590e8`](https://github.com/DS4SD/docling-core/commit/c6590e83e28626e4a6b62fdbd270cb794bf10918))

## [v2.16.1](https://github.com/DS4SD/docling-core/releases/tag/v2.16.1) - 2025-01-30

### Fix

* Add newline to md formula export ([#142](https://github.com/DS4SD/docling-core/issues/142)) ([`d07a87e`](https://github.com/DS4SD/docling-core/commit/d07a87e1fbc777cd6d01c7646d714a44a69bc123))

## [v2.16.0](https://github.com/DS4SD/docling-core/releases/tag/v2.16.0) - 2025-01-29

### Feature

* Escape underscores that are within latex equations ([#137](https://github.com/DS4SD/docling-core/issues/137)) ([`0d5cd11`](https://github.com/DS4SD/docling-core/commit/0d5cd11326d8521360add6ffaa3de845bf72abe2))
* Add escaping_underscores option to markdown export ([#135](https://github.com/DS4SD/docling-core/issues/135)) ([`c9739b2`](https://github.com/DS4SD/docling-core/commit/c9739b2c6cf0686747fbda5331e1fd1a174bb91f))
* Added the geometric operations to BoundingBox ([#136](https://github.com/DS4SD/docling-core/issues/136)) ([`f02bbae`](https://github.com/DS4SD/docling-core/commit/f02bbaea47ebbfe98265f530b0b62dd2a6ac1ecd))

## [v2.15.1](https://github.com/DS4SD/docling-core/releases/tag/v2.15.1) - 2025-01-21

### Fix

* Backward compatible add_text() ([#132](https://github.com/DS4SD/docling-core/issues/132)) ([`7e45817`](https://github.com/DS4SD/docling-core/commit/7e458179d8ec46017fd90114a55360daf419f926))

## [v2.15.0](https://github.com/DS4SD/docling-core/releases/tag/v2.15.0) - 2025-01-21

### Feature

* Add CodeItem as pydantic type, update export methods and APIs ([#129](https://github.com/DS4SD/docling-core/issues/129)) ([`c940aa5`](https://github.com/DS4SD/docling-core/commit/c940aa5ca9b345333e3e95d8c0ec32ddfa227385))

### Fix

* Fix hybrid chunker token constraint ([#131](https://github.com/DS4SD/docling-core/issues/131)) ([`b741eea`](https://github.com/DS4SD/docling-core/commit/b741eeaab437781e36f9d356478ef525ef54867b))
* Always return a new bbox when changing origin ([#128](https://github.com/DS4SD/docling-core/issues/128)) ([`841668f`](https://github.com/DS4SD/docling-core/commit/841668f416f2079afc6f8ab07e5507aacce59de3))

## [v2.14.0](https://github.com/DS4SD/docling-core/releases/tag/v2.14.0) - 2025-01-10

### Feature

* Dev/add labels for pictures-classes ([#127](https://github.com/DS4SD/docling-core/issues/127)) ([`078cd61`](https://github.com/DS4SD/docling-core/commit/078cd61b31c36bec553f64c411012e361683bd35))

## [v2.13.1](https://github.com/DS4SD/docling-core/releases/tag/v2.13.1) - 2025-01-08

### Fix

* Restore proper string serialization of DocItemLabel ([#124](https://github.com/DS4SD/docling-core/issues/124)) ([`a52bb88`](https://github.com/DS4SD/docling-core/commit/a52bb88f78146a5777246d3fc04b04d0db1c1631))

## [v2.13.0](https://github.com/DS4SD/docling-core/releases/tag/v2.13.0) - 2025-01-08

### Feature

* Add mapping to colors into DocItemLabel ([#123](https://github.com/DS4SD/docling-core/issues/123)) ([`639f122`](https://github.com/DS4SD/docling-core/commit/639f12226d4d413c5f95dc4989391a209cca1ae6))

### Fix

* Quote referenced URIs in markdown and html ([#122](https://github.com/DS4SD/docling-core/issues/122)) ([`127dd2f`](https://github.com/DS4SD/docling-core/commit/127dd2f6f8862e2c74f821cdb3a1995ee0a243cc))

## [v2.12.1](https://github.com/DS4SD/docling-core/releases/tag/v2.12.1) - 2024-12-17

### Fix

* Fixes for legacy-doc handling ([#115](https://github.com/DS4SD/docling-core/issues/115)) ([`b116c46`](https://github.com/DS4SD/docling-core/commit/b116c465a2af6327cffa95de0745506404cb39f9))

## [v2.12.0](https://github.com/DS4SD/docling-core/releases/tag/v2.12.0) - 2024-12-17

### Feature

* Added the new label comment_section in the groups ([#114](https://github.com/DS4SD/docling-core/issues/114)) ([`5101dd8`](https://github.com/DS4SD/docling-core/commit/5101dd8845dcfc098c7009556e7468478393ea5e))

### Fix

* Skip labels not included in the allow-list ([#113](https://github.com/DS4SD/docling-core/issues/113)) ([`d147c25`](https://github.com/DS4SD/docling-core/commit/d147c2565f635e851b73cd6b97cc78617372b57f))
* Always write with utf8 encoding ([#111](https://github.com/DS4SD/docling-core/issues/111)) ([`268c294`](https://github.com/DS4SD/docling-core/commit/268c294cc95abb36fc491521e39c7bf6e6a45abc))

## [v2.11.0](https://github.com/DS4SD/docling-core/releases/tag/v2.11.0) - 2024-12-16

### Feature

* Add group labels for form and key-value areas ([#110](https://github.com/DS4SD/docling-core/issues/110)) ([`aeaf89d`](https://github.com/DS4SD/docling-core/commit/aeaf89de106201c53066c16963a9d6ba4467e51c))

## [v2.10.0](https://github.com/DS4SD/docling-core/releases/tag/v2.10.0) - 2024-12-13

### Feature

* Add legacy to DoclingDocument utility ([#108](https://github.com/DS4SD/docling-core/issues/108)) ([`b31e0a3`](https://github.com/DS4SD/docling-core/commit/b31e0a3d05cbcf450a4d287484761fc447d3e2ec))
* Add DoclingDocument viewer to CLI ([#99](https://github.com/DS4SD/docling-core/issues/99)) ([`9628d19`](https://github.com/DS4SD/docling-core/commit/9628d19c24ed92834636973c9e272c9a21864604))
* Add default tokenizer to HybridChunker ([#107](https://github.com/DS4SD/docling-core/issues/107)) ([`2591c70`](https://github.com/DS4SD/docling-core/commit/2591c70c66d1615050f47d045c4bc6092f99ebad))

### Fix

* Improve doc item typing ([#105](https://github.com/DS4SD/docling-core/issues/105)) ([`047a196`](https://github.com/DS4SD/docling-core/commit/047a1960afbaed4613b8d305d8dff4988a97c2d9))
* Set origin when merging chunks ([#109](https://github.com/DS4SD/docling-core/issues/109)) ([`b546c0a`](https://github.com/DS4SD/docling-core/commit/b546c0a50d11152f0ad65a1bc59e33478bc11052))
* Add REFERENCE to exported labels and remove CAPTION ([#106](https://github.com/DS4SD/docling-core/issues/106)) ([`a66b0bb`](https://github.com/DS4SD/docling-core/commit/a66b0bb6f8d821bbad738c1bd9fc52317304579f))

## [v2.9.0](https://github.com/DS4SD/docling-core/releases/tag/v2.9.0) - 2024-12-09

### Feature

* Utilities converting document formats ([#91](https://github.com/DS4SD/docling-core/issues/91)) ([`437c498`](https://github.com/DS4SD/docling-core/commit/437c498f77c71cce49c139a25e0803acde429b90))

### Fix

* **markdown:** Preserve underscores in image URLs during markdown export ([#98](https://github.com/DS4SD/docling-core/issues/98)) ([`fd7529f`](https://github.com/DS4SD/docling-core/commit/fd7529f4096ecc5c7809b884c5fef2df9818801f))

## [v2.8.0](https://github.com/DS4SD/docling-core/releases/tag/v2.8.0) - 2024-12-06

### Feature

* Add hybrid chunker ([#68](https://github.com/DS4SD/docling-core/issues/68)) ([`628ab67`](https://github.com/DS4SD/docling-core/commit/628ab679cbcbf4d708619111cd391ff62dc9d080))

## [v2.7.1](https://github.com/DS4SD/docling-core/releases/tag/v2.7.1) - 2024-12-06

### Fix

* Multimodal output ([#96](https://github.com/DS4SD/docling-core/issues/96)) ([`2133af6`](https://github.com/DS4SD/docling-core/commit/2133af61121d202a4df04ef9a28308b82d7c87cb))

## [v2.7.0](https://github.com/DS4SD/docling-core/releases/tag/v2.7.0) - 2024-12-04

### Feature

* Export to OTSL method for docling doc tables ([#86](https://github.com/DS4SD/docling-core/issues/86)) ([`180e294`](https://github.com/DS4SD/docling-core/commit/180e294aada4d97ceeb61556b5f7f310bd078c5f))

## [v2.6.1](https://github.com/DS4SD/docling-core/releases/tag/v2.6.1) - 2024-12-02

### Fix

* Fix circular import ([#87](https://github.com/DS4SD/docling-core/issues/87)) ([`63e6c01`](https://github.com/DS4SD/docling-core/commit/63e6c01863cbf8d71e1636f3dca8226f6bdf63e2))

## [v2.6.0](https://github.com/DS4SD/docling-core/releases/tag/v2.6.0) - 2024-12-02

### Feature

* Extend source resolution with streams and workdir ([#79](https://github.com/DS4SD/docling-core/issues/79)) ([`9a74d13`](https://github.com/DS4SD/docling-core/commit/9a74d13fd60334bd0a4b4687fd5deaaf79b89001))
* Simple method to load DoclingDocument from .json files ([#71](https://github.com/DS4SD/docling-core/issues/71)) ([`fc1cfb0`](https://github.com/DS4SD/docling-core/commit/fc1cfb0fe02914f7c86e357909221ab143d74d4c))

### Fix

* Allow all url types in referenced exports ([#82](https://github.com/DS4SD/docling-core/issues/82)) ([`3bd83bc`](https://github.com/DS4SD/docling-core/commit/3bd83bcfc401f09ed07e7c7f20c51403bf6484d6))
* Even better style for HTML export ([#78](https://github.com/DS4SD/docling-core/issues/78)) ([`8422ad4`](https://github.com/DS4SD/docling-core/commit/8422ad4fbf6ed8372815e0fa9393951f04a759d5))

## [v2.5.1](https://github.com/DS4SD/docling-core/releases/tag/v2.5.1) - 2024-11-27

### Fix

* Hotfix for TableItem.export_to_html args ([#76](https://github.com/DS4SD/docling-core/issues/76)) ([`ae2f131`](https://github.com/DS4SD/docling-core/commit/ae2f1317255938d102c716efaf2db6adbc724bd1))
* Artifacts dir double stem ([#75](https://github.com/DS4SD/docling-core/issues/75)) ([`f93332b`](https://github.com/DS4SD/docling-core/commit/f93332b402c1e175a2df3cad7c254b23591eea34))

## [v2.5.0](https://github.com/DS4SD/docling-core/releases/tag/v2.5.0) - 2024-11-27

### Feature

* Adding HTML export to DoclingDocument, adding export of images in png with links to Markdown & HTML ([#69](https://github.com/DS4SD/docling-core/issues/69)) ([`ef49fd3`](https://github.com/DS4SD/docling-core/commit/ef49fd3f34ce140af20dff8cf48676df20a9502e))

## [v2.4.1](https://github.com/DS4SD/docling-core/releases/tag/v2.4.1) - 2024-11-21

### Fix

* Temporarily force pydantic < 2.10 ([#70](https://github.com/DS4SD/docling-core/issues/70)) ([`289b629`](https://github.com/DS4SD/docling-core/commit/289b629dc9451678885ae30bbcc286290bed5d87))

## [v2.4.0](https://github.com/DS4SD/docling-core/releases/tag/v2.4.0) - 2024-11-18

### Feature

* Add get_image for all DocItem ([#67](https://github.com/DS4SD/docling-core/issues/67)) ([`9d7e831`](https://github.com/DS4SD/docling-core/commit/9d7e831fb23c5069361bcb6be8d562f36393398b))
* Allow exporting a specific page to md. ([#63](https://github.com/DS4SD/docling-core/issues/63)) ([`1a201bc`](https://github.com/DS4SD/docling-core/commit/1a201bc65a32c88bae705b65998ab486b8a4302d))

## [v2.3.2](https://github.com/DS4SD/docling-core/releases/tag/v2.3.2) - 2024-11-11

### Fix

* Fixed selection logic for a slice of the document ([#66](https://github.com/DS4SD/docling-core/issues/66)) ([`dfdc76b`](https://github.com/DS4SD/docling-core/commit/dfdc76bf55a1442d4321b577904c0b4748158b55))

## [v2.3.1](https://github.com/DS4SD/docling-core/releases/tag/v2.3.1) - 2024-11-01

### Fix

* Include titles to chunk heading metadata ([#62](https://github.com/DS4SD/docling-core/issues/62)) ([`bfeb2db`](https://github.com/DS4SD/docling-core/commit/bfeb2db24b70550693911af6aee01db8c74d464a))

## [v2.3.0](https://github.com/DS4SD/docling-core/releases/tag/v2.3.0) - 2024-10-29

### Feature

* Added pydantic models to store charts data (pie, bar, stacked bar, line, scatter) ([#52](https://github.com/DS4SD/docling-core/issues/52)) ([`36b7bea`](https://github.com/DS4SD/docling-core/commit/36b7bea53a291fdd8ffa5fc6cdbe4256d16c8710))

## [v2.2.3](https://github.com/DS4SD/docling-core/releases/tag/v2.2.3) - 2024-10-29

### Fix

* Str representation of enum across python versions ([#60](https://github.com/DS4SD/docling-core/issues/60)) ([`8528918`](https://github.com/DS4SD/docling-core/commit/8528918ae24eb1e50b97935b1136e8e8e2d9717b))
* Title for export to markdown and add text_width parameter ([#59](https://github.com/DS4SD/docling-core/issues/59)) ([`4993c34`](https://github.com/DS4SD/docling-core/commit/4993c3403d0dac869033c38349b785e5c78ac1d9))

## [v2.2.2](https://github.com/DS4SD/docling-core/releases/tag/v2.2.2) - 2024-10-26

### Fix

* Fix non-string table cell handling in chunker ([#58](https://github.com/DS4SD/docling-core/issues/58)) ([`b5d07b2`](https://github.com/DS4SD/docling-core/commit/b5d07b2fa5e865939b9b93a8582eb3207bc48249))

## [v2.2.1](https://github.com/DS4SD/docling-core/releases/tag/v2.2.1) - 2024-10-25

### Fix

* Escaping underscore characters in md export ([#57](https://github.com/DS4SD/docling-core/issues/57)) ([`c344d0f`](https://github.com/DS4SD/docling-core/commit/c344d0fc63ac55068dac5846772e3369f71c771b))

## [v2.2.0](https://github.com/DS4SD/docling-core/releases/tag/v2.2.0) - 2024-10-24

### Feature

* Add headers argument and a custom user-agents for http requests ([#53](https://github.com/DS4SD/docling-core/issues/53)) ([`44941b5`](https://github.com/DS4SD/docling-core/commit/44941b5591fe7db5a2b987f5d2b35785fab386db))

### Fix

* Fix resolution in case of URL without path ([#55](https://github.com/DS4SD/docling-core/issues/55)) ([`2c88e56`](https://github.com/DS4SD/docling-core/commit/2c88e56f8ccb5902457c1749c64c8de6cc963739))

## [v2.1.0](https://github.com/DS4SD/docling-core/releases/tag/v2.1.0) - 2024-10-22

### Feature

* Improve markdown export of DoclingDocument ([#50](https://github.com/DS4SD/docling-core/issues/50)) ([`328778e`](https://github.com/DS4SD/docling-core/commit/328778ed036540ee5fdf0bb16a1b656e5122c5f0))
* Extend chunk meta with schema, version, origin ([#49](https://github.com/DS4SD/docling-core/issues/49)) ([`d09fe7e`](https://github.com/DS4SD/docling-core/commit/d09fe7ed44282b286f9c2588482e515bf40e0fca))

## [v2.0.1](https://github.com/DS4SD/docling-core/releases/tag/v2.0.1) - 2024-10-18

### Fix

* Fix legacy doc ref ([#48](https://github.com/DS4SD/docling-core/issues/48)) ([`e12d6a7`](https://github.com/DS4SD/docling-core/commit/e12d6a70c383a8d3f0c3d73aa6c5eec62a0c3251))
* Add-mimetype-for-asciidocs-markdown ([#47](https://github.com/DS4SD/docling-core/issues/47)) ([`0aab007`](https://github.com/DS4SD/docling-core/commit/0aab0073bbeabe62b2a19e872e108438c199f6c0))

## [v2.0.0](https://github.com/DS4SD/docling-core/releases/tag/v2.0.0) - 2024-10-16

### Feature

* Expose DoclingDocument as main type, move old typing to legacy ([#41](https://github.com/DS4SD/docling-core/issues/41)) ([`03df97f`](https://github.com/DS4SD/docling-core/commit/03df97fa73db2499682613ff17dff9fe996a1bdc))

### Breaking

* Expose DoclingDocument as main type, move old typing to legacy ([#41](https://github.com/DS4SD/docling-core/issues/41)) ([`03df97f`](https://github.com/DS4SD/docling-core/commit/03df97fa73db2499682613ff17dff9fe996a1bdc))

## [v1.7.2](https://github.com/DS4SD/docling-core/releases/tag/v1.7.2) - 2024-10-09

### Fix

* Loosen pandas version ([#40](https://github.com/DS4SD/docling-core/issues/40)) ([`aec1a41`](https://github.com/DS4SD/docling-core/commit/aec1a41402d64c2c216923b40d4521f8d46540b7))

## [v1.7.1](https://github.com/DS4SD/docling-core/releases/tag/v1.7.1) - 2024-10-07

### Fix

* Make doc metadata keys pure strings ([#38](https://github.com/DS4SD/docling-core/issues/38)) ([`246627f`](https://github.com/DS4SD/docling-core/commit/246627f4f6aef1121dd4211cc223f356a133c60e))
* Align chunk ref format with one used in Document ([#37](https://github.com/DS4SD/docling-core/issues/37)) ([`b5592ad`](https://github.com/DS4SD/docling-core/commit/b5592ad747a061cb6b47c86228063371a80a9b44))

## [v1.7.0](https://github.com/DS4SD/docling-core/releases/tag/v1.7.0) - 2024-10-01

### Feature

* (experimental) introduce new document format ([#21](https://github.com/DS4SD/docling-core/issues/21)) ([`688789e`](https://github.com/DS4SD/docling-core/commit/688789ea751d75c15a6957dba4ba496b899e9d11))
* Add doc metadata extractor and ID generator classes ([#34](https://github.com/DS4SD/docling-core/issues/34)) ([`b76780c`](https://github.com/DS4SD/docling-core/commit/b76780c3b21a89d407b6afb5e72cd4f46dbcf569))
* Support heading as chunk metadata ([#36](https://github.com/DS4SD/docling-core/issues/36)) ([`4bde515`](https://github.com/DS4SD/docling-core/commit/4bde51528d23be9bed797030a75991f6acdb241f))

## [v1.6.3](https://github.com/DS4SD/docling-core/releases/tag/v1.6.3) - 2024-09-26

### Fix

* Change order of JSON Schema to search mapper transformations ([#32](https://github.com/DS4SD/docling-core/issues/32)) ([`a4ddd14`](https://github.com/DS4SD/docling-core/commit/a4ddd142eef864c55b62c8815d38dbff14f4caa7))

## [v1.6.2](https://github.com/DS4SD/docling-core/releases/tag/v1.6.2) - 2024-09-24

### Fix

* Remove duplicate captions in markdown ([#31](https://github.com/DS4SD/docling-core/issues/31)) ([`a334b9f`](https://github.com/DS4SD/docling-core/commit/a334b9fc721a2e1efc9f12b585cff17363875d57))

## [v1.6.1](https://github.com/DS4SD/docling-core/releases/tag/v1.6.1) - 2024-09-24

### Fix

* Remove unnecessary package dependency ([#30](https://github.com/DS4SD/docling-core/issues/30)) ([`e706d68`](https://github.com/DS4SD/docling-core/commit/e706d686db159f6480439d214c85b1664f38e28f))

## [v1.6.0](https://github.com/DS4SD/docling-core/releases/tag/v1.6.0) - 2024-09-23

### Feature

* Add figures in markdown export ([#27](https://github.com/DS4SD/docling-core/issues/27)) ([`b843ae6`](https://github.com/DS4SD/docling-core/commit/b843ae6688a20e68e2da59b2f68fd61f8d4beacb))

## [v1.5.0](https://github.com/DS4SD/docling-core/releases/tag/v1.5.0) - 2024-09-20

### Feature

* Add export to doctags for document components ([#25](https://github.com/DS4SD/docling-core/issues/25)) ([`891530f`](https://github.com/DS4SD/docling-core/commit/891530f595dbf656bbc2708fb25a05aa1ec65afa))
* Add file source resolution utility ([#22](https://github.com/DS4SD/docling-core/issues/22)) ([`752cbc3`](https://github.com/DS4SD/docling-core/commit/752cbc3e89461fa633277cfe3887bc5a6fa5c2b0))

## [v1.4.1](https://github.com/DS4SD/docling-core/releases/tag/v1.4.1) - 2024-09-18

### Fix

* Add export to xml and html ([#17](https://github.com/DS4SD/docling-core/issues/17)) ([`9bc256e`](https://github.com/DS4SD/docling-core/commit/9bc256e5bbbe02cc0a317bc2920c8e0becb3090c))

## [v1.4.0](https://github.com/DS4SD/docling-core/releases/tag/v1.4.0) - 2024-09-18

### Feature

* Add table exporters ([#20](https://github.com/DS4SD/docling-core/issues/20)) ([`2cc2429`](https://github.com/DS4SD/docling-core/commit/2cc2429e2731998c3282ba133995439450f08574))

## [v1.3.0](https://github.com/DS4SD/docling-core/releases/tag/v1.3.0) - 2024-09-11

### Feature

* Add hierarchical chunker ([#18](https://github.com/DS4SD/docling-core/issues/18)) ([`9698d30`](https://github.com/DS4SD/docling-core/commit/9698d30288df17ecde67f170848f1be47cd97d33))

## [v1.2.0](https://github.com/DS4SD/docling-core/releases/tag/v1.2.0) - 2024-09-10

### Feature

* Added the XML export ([#16](https://github.com/DS4SD/docling-core/issues/16)) ([`acdf816`](https://github.com/DS4SD/docling-core/commit/acdf81608134c23969c9e620085f4fff4f42a12f))

## [v1.1.4](https://github.com/DS4SD/docling-core/releases/tag/v1.1.4) - 2024-09-06

### Fix

* Validate_model() could be called with other types rather than dict ([#14](https://github.com/DS4SD/docling-core/issues/14)) ([`235b2cd`](https://github.com/DS4SD/docling-core/commit/235b2cd10b595c813c03db5b4effbc7cc2feaaf0))

### Documentation

* Update link to Docling ([#12](https://github.com/DS4SD/docling-core/issues/12)) ([`aaf17fe`](https://github.com/DS4SD/docling-core/commit/aaf17fe0f6eae7ee21c54c56fded05f24ec936b1))

## [v1.1.3](https://github.com/DS4SD/docling-core/releases/tag/v1.1.3) - 2024-08-28

### Fix

* Use same base type for all components ([#10](https://github.com/DS4SD/docling-core/issues/10)) ([`f450c8c`](https://github.com/DS4SD/docling-core/commit/f450c8cbfd623bf5c7013bae956d23618004f43d))

## [v1.1.2](https://github.com/DS4SD/docling-core/releases/tag/v1.1.2) - 2024-07-31

### Fix

* Make page number strictly positive ([#8](https://github.com/DS4SD/docling-core/issues/8)) ([`ec3cff9`](https://github.com/DS4SD/docling-core/commit/ec3cff97e5079251087cd7b4b42e8c509cd244f3))

## [v1.1.1](https://github.com/DS4SD/docling-core/releases/tag/v1.1.1) - 2024-07-23

### Fix

* Set type to optional ([#7](https://github.com/DS4SD/docling-core/issues/7)) ([`faf472c`](https://github.com/DS4SD/docling-core/commit/faf472c1689746adc43e0ae8ef6d6e3fcf87c023))

### Documentation

* Revamp installation instructions ([#6](https://github.com/DS4SD/docling-core/issues/6)) ([`3f77b2e`](https://github.com/DS4SD/docling-core/commit/3f77b2e92c415c7290df8c4d534ba3455dbe62bd))

## [v1.1.0](https://github.com/DS4SD/docling-core/releases/tag/v1.1.0) - 2024-07-18

### Feature

* Add document Markdown export ([#4](https://github.com/DS4SD/docling-core/issues/4)) ([`d0ffc85`](https://github.com/DS4SD/docling-core/commit/d0ffc85e0c2b49d201f5359c4dc4efb5cd5716b0))

## [v1.0.0](https://github.com/DS4SD/docling-core/releases/tag/v1.0.0) - 2024-07-17

### Feature

* Trigger v1.0.0 release ([#3](https://github.com/DS4SD/docling-core/issues/3)) ([`daece4c`](https://github.com/DS4SD/docling-core/commit/daece4ceae363351072aa7e0adb91037e0dd7b66))

### Breaking

* trigger v1.0.0 release ([#3](https://github.com/DS4SD/docling-core/issues/3)) ([`daece4c`](https://github.com/DS4SD/docling-core/commit/daece4ceae363351072aa7e0adb91037e0dd7b66))

## [v0.0.1](https://github.com/DS4SD/docling-core/releases/tag/v0.0.1) - 2024-07-17

### Fix

* Fix definition issues in record type ([#2](https://github.com/DS4SD/docling-core/issues/2)) ([`656f563`](https://github.com/DS4SD/docling-core/commit/656f56380f603c3de125f6c59554f26ac8cd0a78))
