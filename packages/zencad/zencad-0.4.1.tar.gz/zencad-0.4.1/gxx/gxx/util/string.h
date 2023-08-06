#ifndef GXX_STRING_H
#define GXX_STRING_H

#include <list>
#include <vector>
#include <string>

namespace gxx {
	using strvec = std::vector<std::string>;
	using strlst = std::list<std::string>;

	strvec split(const std::string& str, char delim);
	std::string join(const strvec&, char delim);

	static inline std::string serialstr8(const std::string& str) {
		std::string ret;
		ret.push_back((uint8_t)str.size());
		ret.append(str);
		return ret;
	}

	static inline std::string serialstr8(const char* data, size_t size) {
		std::string ret;
		ret.push_back((uint8_t) size);
		ret.append(data, size);
		return ret;
	}
}

#endif