add_ngsolve_python_module(ngsxfem_xfem_py python_xfem.cpp)
set_target_properties(ngsxfem_xfem_py PROPERTIES INSTALL_RPATH "${NETGEN_RPATH_TOKEN}/../${NETGEN_PYTHON_RPATH}")

if(SETUP_PY)
  install(TARGETS ngsxfem_xfem_py DESTINATION ${CMAKE_INSTALL_PREFIX}/python)
  # quick and very dirty hack...
  set_target_properties(ngsxfem_xfem_py PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR};/usr/local/lib;/usr/lib;~/.local/lib")
else(SETUP_PY)
  install(TARGETS ngsxfem_xfem_py DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem)
endif(SETUP_PY)
target_link_libraries(ngsxfem_xfem_py ngsxfem_xfem)
#ngsxfem_lsetcurving ngsxfem_utils ngsxfem_cutint ngsxfem_xfem)

add_library(ngsxfem_xfem ${NGS_LIB_TYPE}
  cutinfo.cpp
  ghostpenalty.cpp
  xFESpace.cpp
  sFESpace.cpp
  xfemdiffops.cpp
  xfiniteelement.cpp
  symboliccutbfi.cpp
  symboliccutlfi.cpp
  python_xfem.cpp
  )

set_target_properties(ngsxfem_xfem PROPERTIES SUFFIX ".so")

target_link_libraries(ngsxfem_xfem ngsxfem_cutint ${PYTHON_LIBS} ${LAPACK_LIBRARIES} ${NETGEN_LIBS})

if(SETUP_PY)
  install(TARGETS ngsxfem_xfem DESTINATION lib)
  set_target_properties(ngsxfem_utils PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR}")
else(SETUP_PY)
  install(TARGETS ngsxfem_xfem DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem)
endif(SETUP_PY)

install( FILES
  cutinfo.hpp
  ghostpenalty.hpp
  xFESpace.hpp
  sFESpace.hpp
  xfemdiffops.hpp
  xfiniteelement.hpp
  symboliccutbfi.hpp
  symboliccutlfi.hpp
  DESTINATION include
  )

