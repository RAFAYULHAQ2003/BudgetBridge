# def groupcreation(group_name,permissions):
#     """
#     Utility function to create a group with the specified name.
#     """
#     group, created = Group.objects.get_or_create(name=group_name)
#     group.permissions.set(permissions.all())
#     return group