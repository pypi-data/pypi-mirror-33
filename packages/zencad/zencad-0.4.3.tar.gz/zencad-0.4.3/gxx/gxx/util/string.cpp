#include <gxx/util/string.h>

namespace gxx {
	strvec split(const std::string& str, char delim) {
		gxx::strvec outvec;
	
		char* strt;
		char* ptr = (char*)str.data();
		char* end = (char*)str.data() + str.size();
		
		while(true) {
			while (*ptr == delim) ptr++;
			if (ptr == end) break;
		
			strt = ptr;
			while (*ptr != delim && ptr != end) ptr++;
			outvec.emplace_back(strt, ptr - strt);		
		}
	
		return outvec;
	}

	std::string join(const gxx::strvec& vec, char delim) {
		if (vec.size() == 0) {
			return "";
		}

		std::string ret;

		size_t len = 0;
		for (auto& s : vec) {
			len ++;
			len += s.size();  
		}
		ret.reserve(len);

		auto preend = vec.end();
		auto iter = vec.begin();
		preend--;
		for (; iter != preend; iter++) {
			ret.append(*iter);
			ret.push_back(delim);
		}
		ret.append(*iter);

		return ret;
	}  
}