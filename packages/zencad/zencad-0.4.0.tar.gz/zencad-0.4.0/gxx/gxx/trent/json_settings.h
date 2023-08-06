#ifndef GXX_JSON_SETTINGS_H
#define GXX_JSON_SETTINGS_H

#include <string>
#include <sstream>
#include <fstream>

#include <gxx/trent/json.h>
#include <gxx/trent/settings.h>

namespace gxx {
	class json_settings : public trent_settings {
		std::string pathstr;

	public:
		ACCESSOR(path, pathstr);

		json_settings() = default;
		json_settings(const std::string& str) : pathstr(str) {};

private:
		void load() {
			std::fstream file(pathstr);
			if (!file.good()) return;
			std::stringstream file_contents;
			file_contents << file.rdbuf();
			tr = json::parse(file_contents).unwrap();
			file.close();
                        gxx::println("sync", tr);
                        synced = true;
		}
		
public:
		void sync() {
			load();
		}

		void save() override {
			std::fstream file(pathstr, std::ios_base::trunc | std::ios::out);
			if (!file.good()) {
				PANIC_TRACED();
			}
			json::pretty_print_to(tr, file);	
			file.close();
		}
	};
}

#endif
