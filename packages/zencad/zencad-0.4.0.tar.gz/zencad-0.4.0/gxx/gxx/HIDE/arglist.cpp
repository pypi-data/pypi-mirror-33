#include <gxx/arglist.h>

namespace gxx {	
	const argument& arglist::operator[](int i) const {
		return list[i];
	}

	argument* arglist::begin() { return list; }
	argument* arglist::end() { return list + listsz; }	
/*
	const char* argument::type_to_string() {
		switch (type) {
			case SInt8: return "SInt8";
			case SInt16: return "SInt16";
			case SInt32: return "SInt32";
			case SInt64: return "SInt64";
			case UInt8: return "UInt8";
			case UInt16: return "UInt16";
			case UInt32: return "UInt32";
			case UInt64: return "UInt64";
			case CharPtr: return "CharPtr";
			case CustomType: return "Custom";
			default: return "Undeclared";
		}
	}
*/
	int arglist::find_name(const char* name, size_t len) const {
        for(uint8_t i = 0; i < listsz; ++i) {
			if (list[i].name && !strncmp(name, list[i].name, len)) return i; 
		}
		return -1;
	}
}
