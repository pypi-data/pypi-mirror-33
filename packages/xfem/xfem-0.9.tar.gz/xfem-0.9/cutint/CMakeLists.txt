add_ngsolve_python_module(ngsxfem_cutint_py python_cutint.cpp)
if(SETUP_PY)
  install(TARGETS ngsxfem_cutint_py DESTINATION ${CMAKE_INSTALL_PREFIX}/python)
  # quick and very dirty hack...
  set_target_properties(ngsxfem_cutint_py PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR};/usr/local/lib;/usr/lib;~/.local/lib")
else(SETUP_PY)
  set_target_properties(ngsxfem_cutint_py PROPERTIES INSTALL_RPATH "${NETGEN_RPATH_TOKEN}/../${NETGEN_PYTHON_RPATH}")
  install( TARGETS ngsxfem_cutint_py DESTINATION ${ngs_install_dir})
endif(SETUP_PY)
target_link_libraries(ngsxfem_cutint_py ngsxfem_cutint)

add_library(ngsxfem_cutint ${NGS_LIB_TYPE}
  fieldeval.cpp fieldeval.hpp
  xintegration.hpp xintegration.cpp
  xdecompose.cpp xdecompose.hpp  
  straightcutrule.hpp straightcutrule.cpp
  spacetimecutrule.hpp spacetimecutrule.cpp
        )

set_target_properties(ngsxfem_cutint PROPERTIES SUFFIX ".so")

target_link_libraries(ngsxfem_cutint ngsxfem_utils ngsxfem_spacetime ${PYTHON_LIBS} ${LAPACK_LIBRARIES} ${NETGEN_LIBS})
if(SETUP_PY)
  install(TARGETS ngsxfem_cutint DESTINATION lib)
  set_target_properties(ngsxfem_cutint PROPERTIES INSTALL_RPATH "${NGSOLVE_LIBRARY_DIR}")
else(SETUP_PY)
  install( TARGETS ngsxfem_cutint DESTINATION ${ngs_install_dir})
endif(SETUP_PY)

add_subdirectory(py_demos)

