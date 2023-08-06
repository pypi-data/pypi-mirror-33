from .moduleutils import cherry_pick


__version__ = '0.1.2'


# map of functions with modules to be cherry-picked.
__attr_map__ = (
    'flutils.objutils:has_any_attrs',
    'flutils.objutils:has_any_callables',
    'flutils.objutils:has_attrs',
    'flutils.objutils:has_callables',
    'flutils.objutils:is_list_like',
    'flutils.objutils:is_subclass_of_any',
    'flutils.pathutils:chmod',
    'flutils.pathutils:chown',
    'flutils.pathutils:directory_present',
    'flutils.pathutils:exists_as',
    'flutils.pathutils:find_paths',
    'flutils.pathutils:get_os_group',
    'flutils.pathutils:get_os_user',
    'flutils.pathutils:normalize_path',
    'flutils.pathutils:path_absent',
    'flutils.setuputils:add_coverage_command_to_setup',
    'flutils.setuputils:add_style_command_to_setup',
    'flutils.setuputils:add_lint_command_to_setup',
    'flutils.setuputils:add_pipeline_tests_command_to_setup',
    'flutils.strutils:camel_to_underscore',
    'flutils.strutils:underscore_to_camel',
    'flutils.validators:validate_identifier',
    # Because cherry_pick was imported above, cherry_pick's
    # submodule must be added below.
    'flutils.moduleutils',
    'flutils.moduleutils:cherry_pick',
    'flutils.moduleutils:lazy_import_module'
)

cherry_pick(globals())
