add_ngsolve_python_module(ngsxfem_lsetcurving_py python_lsetcurving.cpp)
if(SETUP_PY)
  install(TARGETS ngsxfem_lsetcurving_py DESTINATION ${CMAKE_INSTALL_PREFIX}/python)
  # quick and very dirty hack...
  set_target_properties(ngsxfem_lsetcurving_py PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR};/usr/local/lib;/usr/lib;~/.local/lib")
else(SETUP_PY)
  set_target_properties(ngsxfem_lsetcurving_py PROPERTIES INSTALL_RPATH "${NETGEN_RPATH_TOKEN}/../${NETGEN_PYTHON_RPATH}")
  install(TARGETS ngsxfem_lsetcurving_py DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem)
endif(SETUP_PY)
target_link_libraries(ngsxfem_lsetcurving_py ngsxfem_lsetcurving ngsxfem_utils)

add_library(ngsxfem_lsetcurving ${NGS_LIB_TYPE}
  shiftintegrators.cpp calcpointshift.cpp calcgeomerrors.cpp lsetrefine.cpp
  projshift.cpp shiftedevaluate.cpp
  )


install( FILES
  shiftintegrators.hpp calcpointshift.hpp calcgeomerrors.hpp lsetrefine.hpp
  projshift.hpp shiftedevaluate.hpp
  DESTINATION include
  )

target_link_libraries(ngsxfem_lsetcurving ngsxfem_xfem ${PYTHON_LIBS} ${LAPACK_LIBRARIES} ${NETGEN_LIBS})

if(SETUP_PY)
  install( TARGETS ngsxfem_lsetcurving DESTINATION lib)
  set_target_properties(ngsxfem_lsetcurving PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR}")
else(SETUP_PY)
  install( TARGETS ngsxfem_lsetcurving DESTINATION ${ngs_install_dir})
endif(SETUP_PY)

# install ( FILES lsetcurv.py DESTINATION python)

if (NOT SETUP_PY)
  install (FILES
    lsetcurv.py
    DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem
    COMPONENT xfem
    )
endif(NOT SETUP_PY)

add_subdirectory(py_demos)

