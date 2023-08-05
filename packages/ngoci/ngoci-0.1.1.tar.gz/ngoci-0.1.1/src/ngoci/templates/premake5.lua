{% from 'ngomf/macros_python.py' import protected_region %}

dofile (path.join(os.getenv("DIR_SCRIPTS_ROOT"),"premake5_common.lua"))

workspace "{{project.name}}" 

    SolutionConfiguration()
    defines {
        {% for dep in deps %}
        "{{dep.macroPrefix}}_USE_DYN",
        {% endfor %}
        "{{project.macroPrefix}}_USE_DYN"
    }
    local _exportSymbol = "{{project.macroPrefix}}_MAKE_DLL"
    links { 
        {% for dep in deps %}
        "{{dep.name}}"{{ "," if not loop.last }}
        {% endfor %}
    }
    {{ protected_region(project.name+'.premake.solution', user_code, '    --') }}
    {% if project.RlmLicFeature %}
    LicenseOptions()
    {% endif %}

project "{{project.name}}"

    PrefilterSharedLibBuildOptions("{{project.name}}")
    defines {_exportSymbol}
    {{ protected_region(project.name+'.premake.sharedlib', user_code, '   --') }}

    FilterSharedLibBuildOptions("{{project.name}}")


    
{% if project.hasTest %}

project "test_{{project.name}}"

    PrefilterTestBuildOptions("test_{{project.name}}")
    links { "{{project.name}}"}
    {{ protected_region(project.name+'.premake.test', user_code, '    --') }}

    FilterTestBuildOptions("test_{{project.name}}")

{% endif %}