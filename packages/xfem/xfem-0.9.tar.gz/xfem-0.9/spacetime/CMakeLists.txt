add_ngsolve_python_module(ngsxfem_spacetime_py python_spacetime.cpp)
set_target_properties(ngsxfem_spacetime_py PROPERTIES INSTALL_RPATH "${NETGEN_RPATH_TOKEN}/../${NETGEN_PYTHON_RPATH}")

if(SETUP_PY)
  install(TARGETS ngsxfem_spacetime_py DESTINATION ${CMAKE_INSTALL_PREFIX}/python)
  # quick and very dirty hack...
  set_target_properties(ngsxfem_spacetime_py PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR};/usr/local/lib;/usr/lib;~/.local/lib")
else(SETUP_PY)
  install(TARGETS ngsxfem_spacetime_py DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem)
endif(SETUP_PY)
target_link_libraries(ngsxfem_spacetime_py ngsxfem_spacetime ngsxfem_cutint ngsxfem_utils)

add_library(ngsxfem_spacetime ${NGS_LIB_TYPE}
  SpaceTimeFE.cpp
  SpaceTimeFESpace.cpp
  diffopDt.cpp
  timecf.cpp
)

set_target_properties(ngsxfem_spacetime PROPERTIES SUFFIX ".so")

if(NOT WIN32)
  target_link_libraries(ngsxfem_spacetime ngsxfem_utils ${PYTHON_LIBS} ${LAPACK_LIBRARIES} ${NETGEN_LIBS})
  if(SETUP_PY)
    install( TARGETS ngsxfem_spacetime DESTINATION lib)
    set_target_properties(ngsxfem_utils PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR}")
  else(SETUP_PY)
    install( TARGETS ngsxfem_spacetime DESTINATION ${ngs_install_dir})
  endif(SETUP_PY)
endif(NOT WIN32)


install( FILES
  SpaceTimeFE.hpp
  SpaceTimeFESpace.hpp
  diffopDt.hpp
  timecf.hpp
  DESTINATION include
)
if(NOT SETUP_PY)
  install (FILES
    lset_spacetime.py
    DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem
    COMPONENT xfem
    )
endif(NOT SETUP_PY)


install( FILES
  py_demos/spacetime_P1P1.py
  DESTINATION share/ngsxfem
)
