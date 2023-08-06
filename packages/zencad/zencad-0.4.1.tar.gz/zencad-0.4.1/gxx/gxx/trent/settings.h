#ifndef GXX_TRENT_SETTINGS_H
#define GXX_TRENT_SETTINGS_H

//#include <gxx/print/printable.h>
#include <gxx/trent/trent.h>

namespace gxx {
	struct trent_settings {
		gxx::trent tr;
		bool synced = false;

		virtual void sync() = 0;
		virtual void save() = 0;
	
		gxx::trent& node() { return tr; }
		const gxx::trent& node() const { return tr; }
	};

	struct trent_settings_slice : public trent_settings {
		gxx::trent_settings& settings;
		gxx::trent_path path;

		trent_settings_slice(gxx::trent_settings& stgs, const gxx::trent_path& path) 
                        : settings(stgs), path(path) {

                    //gxx::println("here", stgs.synced);
                }
		
		void sync() {
                        //gxx::println("here", settings.synced);
			if (!settings.synced) {
                            //gxx::println("here");
				settings.sync();
			}
			tr = settings.node()[path];
                        synced = true;
		}

		void save() {
			//bind = tr;
                        settings.node()[path] = tr;
			settings.save();
		}
	};


	/*class trent_settings_basic {
	public:
		virtual gxx::trent& at(const std::string& str) = 0;
		virtual gxx::trent& operator[](const std::string& str) = 0;
        virtual const gxx::trent& operator[](const std::string& str) const = 0;
		virtual gxx::trent& operator[](int i) = 0;
        //virtual const gxx::trent& operator[](int i) const = 0;

		virtual bool ok() = 0;
		virtual void save() = 0;
		virtual void sync() = 0;
		virtual trent& node() = 0;
                virtual const trent& node() const = 0;
	};

	class settings_slice : public trent_settings_basic {
		trent_settings_basic* base;
		std::string name;
		gxx::trent* rt = nullptr;

	public:
		settings_slice(trent_settings_basic& base, const std::string name) : base(&base), name(name) {}

		gxx::trent& at(const std::string& str) override {
			PANIC_TRACED();
		}

		gxx::trent& operator[](const std::string& str) override {
			return node()[str];
		}

        const gxx::trent& operator[](const std::string& str) const override {
            return node()[str];
        }

        gxx::trent& operator[](int i) override {
			return node()[i];
		}

        //const gxx::trent& operator[](int i) const override {
        //    return node()[i];
        //}
		
		/*
		gxx::trent& create(const std::string& str, const std::string&) override {
			PANIC_TRACED();
		}

		gxx::trent& create(const std::string& str, int) override {
			PANIC_TRACED();
		}*/

	/*	void save() override {
			base->save();
		}

		bool ok() override {
			return (rt && rt->is_dict());
		}

		trent& node() {
			return *rt;
		}

                const trent& node() const {
                        return *rt;
                }

                void sync() override {
			if (base->ok()) {
				rt = &(*base)[name];
				if (!rt->is_dict()) {
					gxx::println("create new slice");
					*rt = gxx::trent(gxx::trent::type::dict);
					save();
				}
			} else {
				PANIC_TRACED();
			}
		}
	};
*/
        class settings_binder_integer : public trent_settings_slice {
	public:
                settings_binder_integer(trent_settings& base, const trent_path& name) : trent_settings_slice(base, name) {}

		void sync_default(trent::integer_type def) {
                        sync();
                    //tr = &node()[name];
                        if (node().is_nil()) node() = def;
		}

                settings_binder_integer& operator=(int64_t i) {
                        node() = i;
                        return *this;
                }

                /*settings_binder_integer& operator++() {
                        node() = (*tr).as_integer() + 1;
			return *this;
		}

		settings_binder_integer& operator++(int) {
			*tr = (*tr).as_integer() + 1;
			return *this;
                }*/

                operator trent::integer_type() const { return node().as_integer(); }
	};
       }
/*
        class settings_binder_intvec : public settings_binder, public gxx::array_printable<settings_binder_intvec> {
        public:
                settings_binder_intvec(trent_settings_basic& base, const std::string& name) : settings_binder(base, name) {}

                void sync_default(int size, int64_t def) {
                    tr = &settings[name];
                    tr->as_list().resize(size);
                    for (auto& t: tr->as_list()) {
                        if(!t.is_integer()) t = def;
                    }
                }

                int64_t& operator[](int n) {
                    return tr->operator[](n).unsafe_integer();
                }

                const int64_t& operator[](int n) const {
                    return tr->operator[](n).unsafe_integer();
                }

                size_t size() const { return tr->as_list().size(); }
        };

        class settings_binder_numer : public settings_binder {
	public:
		settings_binder_numer(trent_settings_basic& base, const std::string& name) : settings_binder(base, name) {}

		void sync_default(trent::numer_type def) {
			tr = &settings[name];
			if (tr->is_nil()) *tr = def; 
		}

		settings_binder_numer& operator+=(const trent::numer_type& add) {
			*tr = (*tr).as_numer() + add;
			return *this;
		}

		operator trent::numer_type() const { return tr->as_numer(); }
	};
}
*/
#endif
