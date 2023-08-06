#ifndef GXX_UTIL_GMSG_H
#define GXX_UTIL_GMSG_H

//Определение стаффирующих байтов для протокола gstuff.

namespace gxx {
	namespace gmsg {
		constexpr char strt = 0xAC;
		constexpr char stub = 0xAD;
		constexpr char stub_strt = 0xAE;
		constexpr char stub_stub = 0xAF;
	} 
}

#endif