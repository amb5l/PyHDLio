# Third-Party Licenses

This document lists all third-party projects and their licenses used in PyHDLio.

## PLY (Python Lex-Yacc)
- **Repository**: https://github.com/dabeaz/ply.git
- **License**: BSD License
- **Usage**: Parser generation toolkit used by PyHDLio
- **Location**: `hdlio/submodules/ply/`

```
Copyright (C) 2001-2018 David M. Beazley (Dabeaz LLC)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the David Beazley or Dabeaz LLC may be used to
  endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Test Projects

Test projects and their licenses are maintained in the companion **PyHDLio-dev** repository. This separation ensures that:

1. **Core Library**: PyHDLio remains lightweight with minimal dependencies
2. **Test Isolation**: Test projects don't affect the core library's licensing
3. **Optional Testing**: Developers can choose which test suites to use
4. **Clean Distribution**: PyHDLio releases don't include test project code

For test project licenses, see the PyHDLio-dev repository:
- `tests/vhdl/` - VHDL test projects (en_cl_fix, osvvm, open-logic)
- `tests/verilog/` - Verilog/SystemVerilog test projects

## License Compliance

### PLY Usage
PLY is used under the BSD license, which is:
- **Permissive**: Commercial-friendly
- **Attribution**: Requires copyright notice retention
- **No Copyleft**: Does not affect PyHDLio's licensing terms

### No License Contamination
The use of PLY does not affect PyHDLio's own licensing terms. PyHDLio remains under its original license.

For the complete PLY license text, see: `hdlio/submodules/ply/README.md`