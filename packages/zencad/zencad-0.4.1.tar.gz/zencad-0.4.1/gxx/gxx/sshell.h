#ifndef GXX_SIMPLE_SHELL_H
#define GXX_SIMPLE_SHELL_H

#include <gxx/datastruct/argvc.h>
#include <gxx/event/delegate.h>

namespace gxx{

	/*class sshell_record {
	public:
		hlist_node hlnk;
		const char* name;
		delegate<int, int, char**> dlg;

		sshell_record(const char* name, delegate<int, int, char**> dlg) :
			name(name), dlg(dlg) { }
		static const char*& getkey(sshell_record& rec) { return rec.name; }
	};*/
	struct sshell {
		struct command {
			const char* name;
			int (*func) (int, const char**);
		};

		command* table;
		size_t table_size;

		void settable(command* tbl, size_t size) {
			table = tbl;
			table_size = size;
		}

	//public:
		//gxx::static_hashtable<10, sshell_record, const char*, &sshell_record::hlnk> table;

	//public:
		static constexpr uint8_t OK = 0;
		static constexpr uint8_t FunctionNotExist = -1;
		static constexpr uint8_t EmptyString = -2;
//		static constexpr uint8_t WrongArgsTotal = -3;
//		static constexpr uint8_t WrongArgsData = -4;
//		static constexpr uint8_t InternalError = -5;

	/*	void add(const char* name, delegate<int, int, char**> dlg) {
			auto node = new sshell_record(name, dlg);
			table.put(*node);
		};

		void add(const char* name, delegate<int> vdlg) {
			delegate<int, int, char**> dlg;
			memcpy(&dlg, &vdlg, sizeof(vdlg));
			auto node = new sshell_record(name, dlg);
			table.put(*node);
		};

		void add(const char* name, int(*func)()) {
			auto node = new sshell_record(name, gxx::delegate<int, int, char**>(reinterpret_cast<int(*)(int, char**)>(func)));
			table.put(*node);
		};

		void add(const char* name, int(*func)(int, char**)) {
			auto node = new sshell_record(name, gxx::delegate<int, int, char**>(func));
			table.put(*node);
		};
*/
		int __execute_nosafe(char* str, int* ret) {
			str_argvc_t str_argvc(str);

			auto argc = str_argvc.argc();
			auto argv = str_argvc.argv();

			if (strlen(str) == 0)  {
				return EmptyString;
			}

			for(int i = 0; i < table_size; ++i) {
				if (!strcmp(argv[0], table[i].name)) {
					int res = table[i].func(argc, argv);
					if (ret) *ret = res;
					return OK;
				}
			}

			return FunctionNotExist;
		}

		int execute(const char* _str, int* ret = nullptr) {
			char str[128];
			strcpy(str,_str);
			return __execute_nosafe(str, ret);
		}

		int execute(const char* _str, int len, int* ret = nullptr) {
			char str[128];
			memcpy(str,_str,len);
			str[len] = 0;
			return __execute_nosafe(str, ret);
		}

/*		static const char* strerr(int retcode) {
			switch (retcode) {
				case OK:
					return "RetCodeOK";
				case EmptyString:
					return "EmptyString";
				case FunctionNotExist:
					return "FunctionNotExist";
				case WrongArgsTotal:
					return "WrongArgsTotal";
				case WrongArgsData:
					return "WrongArgsData";
				case InternalError:
					return "InternalError";
				default:
					return "UnregistredRetCode";
			};
		};*/
	};
}

#endif
