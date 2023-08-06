#include <gxx/string.h> 

namespace gxx {
	gxx::strvec split(gxx::string str, char delim) {
		return str.split(delim);
	}
}