from licant.modules import implementation

implementation("gxx.dprint", "stub", 
	sources = "dprint_func_stub.c dprint_stub.c dprintxx.cpp".split(" ")
)

implementation("gxx.dprint", "diag", 
	sources = "dprint_func_impl.c dprint_diag.c assembler.c dprintxx.cpp".split(" "),
	cc_flags = "-Wno-pointer-to-int-cast",
	depends = "gxx.diag",
)

implementation("gxx.dprint", "manually", 
	sources = "dprint_func_impl.c dprint_manually.c assembler.c dprintxx.cpp".split(" ")
)

implementation("gxx.dprint", "cout",
	sources = "dprint_func_impl.c dprint_stdout.c assembler.c dprintxx.cpp".split(" ")
)

implementation("gxx.dprint", "stdout",
	sources = "dprint_func_impl.c dprint_stdout.c assembler.c dprintxx.cpp".split(" ")
)

implementation("gxx.debug.delay", "configure",
	sources = "delay_configure.c"
)
