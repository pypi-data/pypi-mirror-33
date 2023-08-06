#include <gxx/trent/trent.h>
#include <gxx/flow/keys.h>
#include <algorithm>

using namespace gxx::result_type;

namespace gxx {

	trent::~trent() {
		invalidate();
	}

	trent::trent() {}

	trent::trent(const trent& other) {
		m_type = other.m_type;
		switch(m_type) {
			case trent::type::string:
				gxx::constructor(&m_str, other.m_str);
				return;
            case trent::type::list:
				gxx::constructor(&m_arr, other.m_arr);
				return;
            case trent::type::dict:
				gxx::constructor(&m_dict, other.m_dict);
                return;
            case trent::type::numer:
                m_num = other.m_num;
				return;
            case trent::type::integer:
                m_int = other.m_int;
				return;
            case trent::type::nil:
				return;
		}
	}

	//trent::trent(const std::string& str) { init(str); }
	//trent::trent(const char* str) { init(str); }
	//trent::trent(const trent::type& t) { init(t); }
    //trent::trent(const float& i) { init(i); }
    //trent::trent(const double& i) { init(i); }
    //trent::trent(const long double& i) { init(i); }
    //trent::trent(const signed char& i) { init(i); }
    //trent::trent(const signed short& i) { init(i); }
    //trent::trent(const signed int& i) { init(i); }
    //trent::trent(const signed long& i) { init(i); }
    //trent::trent(const signed long long& i) { init(i); }
    //trent::trent(const unsigned char& i) { init(i); }
    //trent::trent(const unsigned short& i) { init(i); }
    //trent::trent(const unsigned int& i) { init(i); }
    //trent::trent(const unsigned long& i) { init(i); }
    //trent::trent(const unsigned long long& i) { init(i); }

	void trent::init(trent::type t) {
		m_type = t;
		switch(m_type) {
			case trent::type::string:
				gxx::constructor(&m_str);
				return;
            case trent::type::list:
				gxx::constructor(&m_arr);
				return;
            case trent::type::dict:
				gxx::constructor(&m_dict);
                return;
            case trent::type::integer:
            case trent::type::numer:
            case trent::type::nil:
				return;
		}
	}

	void trent::init(const std::string& str) {
		m_type = trent::type::string;
		gxx::constructor(&m_str, str);

	}

	void trent::init(const char* str) {
		m_type = trent::type::string;
		gxx::constructor(&m_str, str);

	}

	void trent::init(const float& n) { m_type = trent::type::numer; m_num = n; }
	void trent::init(const double& n) { m_type = trent::type::numer; m_num = n; }
	void trent::init(const long double& n) { m_type = trent::type::numer; m_num = n; }

	void trent::init(const signed char& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const signed short& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const signed int& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const signed long& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const signed long long& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const unsigned char& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const unsigned short& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const unsigned int& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const unsigned long& n) { m_type = trent::type::integer; m_int = n; }
	void trent::init(const unsigned long long& n) { m_type = trent::type::integer; m_int = n; }

	void trent::invalidate() {
		switch(m_type) {
			case trent::type::string:
				gxx::destructor(&m_str);
				return;
            case trent::type::list:
				gxx::destructor(&m_arr);
				return;
            case trent::type::dict:
				gxx::destructor(&m_dict);
				return;
            case trent::type::nil:
            case trent::type::numer:
				return;
		}
        m_type = trent::type::nil;
	}

	trent& trent::operator[](int i) {
        if (m_type != trent::type::list) init(trent::type::list);
		if(m_arr.size() <= i) m_arr.resize(i + 1);
		return m_arr[i];
	}

	const trent& trent::operator[](int key) const {
        if (m_type != trent::type::list) gxx::panic("wrong trent type");
		return m_arr.at(key);
	}

	trent& trent::operator[](const char* key) {
        if (m_type != trent::type::dict) init(trent::type::dict);
		return m_dict[key];
	}

	trent& trent::operator[](const std::string& key) {
        if (m_type != trent::type::dict) init(trent::type::dict);
		return m_dict[key];
	}

	const trent& trent::operator[](const std::string& key) const {
        if (m_type != trent::type::dict) gxx::panic("wrong trent type");
		return m_dict.at(key);
	}

	trent& trent::operator[](const gxx::buffer& key) {
        if (m_type != trent::type::dict) init(trent::type::dict);
		return m_dict[std::string(key.data(), key.size())];
	}

	const trent& trent::operator[] (const gxx::trent_path& path) const {
		const gxx::trent* tr = this;
		for (const auto& p : path) {
			if (p.is_string) {
				tr = &tr->operator[](p.str);
			}
			else {
				tr = &tr->operator[](p.i32);
			}
		}
		return *tr;
	}

        trent& trent::operator[] (const gxx::trent_path& path) {
                gxx::trent* tr = this;
                for (auto& p : path) {
                        if (p.is_string) {
                                tr = &tr->operator[](p.str);
                        }
                        else {
                                tr = &tr->operator[](p.i32);
                        }
                }
                return *tr;
        }

	const trent& trent::at(int i) const {
		if (m_type != trent::type::list) gxx::panic("wrong trent type");
        if(m_arr.size() <= i) gxx::panic("wrong trent list size");
		return m_arr[i];
	}


        const trent& trent::operator[](const char* key) const {
        if (m_type != trent::type::dict) gxx::panic("wrong trent type");
                return m_dict.at(key);
        }

        /*const trent& trent::at(const char* key) const {
        gxx::println(2);
        if (m_type != trent::type::dict) init(trent::type::dict);
                return m_dict[key];
        }*/

	const trent& trent::at(const std::string& key) const {
        if (m_type != trent::type::dict) gxx::panic("wrong trent type");
		return m_dict.at(key);
	}

	const trent& trent::at(const gxx::buffer& key) const {
        if (m_type != trent::type::dict) gxx::panic("wrong trent type");
		return m_dict.at(std::string(key.data(), key.size()));
	}

	bool trent::have(const std::string& str) const {
        if (m_type != trent::type::dict) gxx::panic("wrong trent type");
		return m_dict.count(str) != 0;
	}

    std::map<std::string, trent>& trent::as_dict() {
        if (m_type != trent::type::dict) init(trent::type::dict);
		return m_dict;
	}

    const std::map<std::string, trent>& trent::as_dict() const {
        if (m_type != trent::type::dict) gxx::panic("wrong_trent_type");
		return m_dict;
	}

    std::vector<trent>& trent::as_list() {
        if (m_type != trent::type::list) init(trent::type::list);
		return m_arr;
	}

    const std::vector<trent>& trent::as_list() const {
        if (m_type != trent::type::list) gxx::panic("wrong_trent_type");
		return m_arr;
	}

    result<std::vector<trent>&> trent::as_list_critical() {
        if (!is_list()) return error("is't list");
		return m_arr;
	}
    result<const std::vector<trent>&> trent::as_list_critical() const {
        if (!is_list()) return error("is't list");
		return m_arr;
    }

	std::string& trent::as_string() {
		if (m_type != trent::type::string) init(trent::type::string);
		return m_str;
	}
	const std::string& trent::as_string() const {
		if (m_type != trent::type::string) gxx::panic("wrong_trent_type");
		return m_str;
	}

	const gxx::buffer trent::as_buffer() const {
		if (m_type == trent::type::string) return gxx::buffer(m_str.data(), m_str.size());
		return gxx::buffer();
	}

    trent::numer_type trent::as_numer() const {
		if (m_type == trent::type::numer) return m_num;
		if (m_type == trent::type::integer) return m_int;
		return 0;
	}

	trent::integer_type trent::as_integer() const {
		if (m_type == trent::type::integer) return m_int;
		return 0;
	}

        result<trent::integer_type>  trent::as_integer_critical() const {
                if (!is_integer()) return error("is't integer");
                return m_int;
        }

	result<std::string&> trent::as_string_critical() {
		if (!is_string()) return error("is't string");
		return m_str;
	}

	result<const std::string&> trent::as_string_critical() const {
		if (!is_string()) return error("is't string");
		return m_str;
	}

    result<trent::numer_type> trent::as_numer_critical() const {
		if (!is_numer()) return error("is't numer");
		return as_numer();
	}

    result<std::map<std::string, trent>&> trent::as_dict_critical() {
        if (!is_dict()) return error("is't dict");
        return as_dict();
	}

    result<const std::map<std::string, trent>&> trent::as_dict_critical() const {
        if (!is_dict()) return error("is't dict");
        return as_dict();
	}

    trent::numer_type trent::as_numer_default(trent::numer_type def) const {
		if (!is_numer()) return def;
		return as_numer();
	}

	std::string& trent::as_string_default(std::string& def) {
		if (!is_string()) return def;
		return m_str;
	}

	bool trent::contains(gxx::buffer buf) {
        if (m_type != type::dict) {
			return false;
		}

		for(const auto& p : m_dict) {
			if (buf == gxx::buffer(p.first.data(), p.first.size())) { 
				return true;
			}
		}

		return false;
	}

	trent::type trent::get_type() const {
		return m_type;
	}

	const char * trent::type_to_str() const {
		switch(m_type) {
            case trent::type::string: 		return "string";
            case trent::type::list: 		return "list";
            case trent::type::dict:         return "dict";
            case trent::type::numer: 		return "numer";
            case trent::type::integer: 		return "integer";
            case trent::type::nil:          return "nil";
		}
	}

	trent& trent::operator= (const trent& other) {
		invalidate();
		m_type = other.m_type;
		switch(m_type) {
			case trent::type::string:
				gxx::constructor(&m_str, other.m_str);
				return *this;
            case trent::type::list:
				gxx::constructor(&m_arr, other.m_arr);
				return *this;
            case trent::type::dict:
				gxx::constructor(&m_dict, other.m_dict);
                return *this;
            case trent::type::numer:
                m_num = other.m_num;
				return *this;
            case trent::type::integer:
                m_int = other.m_int;
				return *this;
            case trent::type::nil:
				return *this;
		}
	}

	trent& trent::operator= (const std::string& str) {
		reset(str);
		return *this;
	}

	trent& trent::operator= (float num) {
		reset(num);
		return *this;
	}

	trent& trent::operator= (double num) {
		reset(num);
		return *this;
	}

	trent& trent::operator= (long double num) {
		reset(num);
		return *this;
	}

	trent& trent::operator= (signed char i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (signed short i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (signed int i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (signed long i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (signed long long i){
		reset(i);
		return *this;
	}


	trent& trent::operator= (unsigned char i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (unsigned short i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (unsigned int i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (unsigned long i){
		reset(i);
		return *this;
	}

	trent& trent::operator= (unsigned long long i){
		reset(i);
		return *this;
	}

	int trent::size() {
        switch(m_type) {
            case trent::type::numer:
			case trent::type::string: return -1;
            case trent::type::list: return m_arr.size();
            case trent::type::dict: return m_dict.size();
		}
	}

	strlst trent::check_dict(strlst lst, check_type ct) {
        if (!is_dict()) return strlst();


		strlst retlist;

        auto _keys = gxx::flow::keys(m_dict);
        strlst keys;//(_keys.begin(), _keys.end());
		for(auto k : _keys) {
			keys.push_back(k);
		}

        lst.sort();
		keys.sort();

		switch (ct) {
			case check_superset:
				std::set_difference(
					keys.begin(), keys.end(),
					lst.begin(), lst.end(),
					std::inserter(retlist, retlist.begin())
				);
				break;

			case check_subset:
				std::set_difference(
					lst.begin(), lst.end(),
					keys.begin(), keys.end(),
					std::inserter(retlist, retlist.begin())
				);
				break;

			case check_equal:
				std::set_symmetric_difference(
					keys.begin(), keys.end(),
					lst.begin(), lst.end(),
					std::inserter(retlist, retlist.begin())
				);
				break;
		}

		return retlist;

	}

	std::pair<strlst, strlst> trent::check_dict_symmetric(strlst lst) {
		std::pair<strlst, strlst> ret;
        if (!is_dict()) return ret;

		auto _keys = gxx::flow::keys(m_dict);
		strlst keys;//(_keys.begin(), _keys.end());
		for(auto k : _keys) {
			keys.push_back(k);
		}

		lst.sort();
		keys.sort();

		std::set_difference(
			keys.begin(), keys.end(),
			lst.begin(), lst.end(),
			std::inserter(ret.first, ret.first.begin())
		);

		std::set_difference(
			lst.begin(), lst.end(),
			keys.begin(), keys.end(),
			std::inserter(ret.second, ret.second.begin())
		);

		return ret;
	}
}
