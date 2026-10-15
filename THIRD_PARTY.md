# Third-party components

Vietify is distributed under the GNU GPL v3 or later (see [LICENSE](LICENSE)).
The components below are used by Vietify. The desktop app bundles the ones
marked *bundled*.

| Component | Use | License | Bundled |
| --- | --- | --- | --- |
| [espeak-ng](https://github.com/espeak-ng/espeak-ng) | phonemization and speech | GPL-3.0 or later | yes |
| [phonemizer](https://github.com/bootphon/phonemizer) | Python wrapper for espeak-ng | GPL-3.0 or later | yes |
| [parsimonious](https://github.com/erikrose/parsimonious) | IPA grammar parser | MIT | yes |
| [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) | drag-and-drop in the GUI | MIT | yes |
| [Pillow](https://python-pillow.org) | speaker icon rendering | MIT-CMU (HPND) | yes |
| [PyInstaller](https://pyinstaller.org) | builds the desktop app | GPL-2.0 or later, with a bootloader exception | build tool only |
| Python and Tcl/Tk | runtime | PSF License; Tcl/Tk license | yes |
| [ipa-to-vie](https://github.com/vuadu/ipa-to-vie) by Rezza Inc. | original project this work is based on | MIT | no (source only) |

## ipa-to-vie notice (MIT)

Vietify is based on ipa-to-vie. Its MIT license requires that the copyright
notice and permission text be kept in copies of substantial portions of the
code:

> [Paste the exact copyright line and MIT license text from
> https://github.com/vuadu/ipa-to-vie/blob/main/LICENSE here.]

## espeak-ng data

The desktop app ships the espeak-ng voice data (`espeak-ng-data`). It is
covered by the same GPL-3.0 terms as espeak-ng.
