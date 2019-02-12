
**************************
django CMS Version Locking
**************************

Explanation
-----------
The version-locking addon is intended to modify the way djangocms-versioning works in the following way: 

 - The primary change is that it locks a version to its author when a draft is created. 
 - That version becomes automatically unlocked again once it is published. 
 - The lock prevents editing of the file by anyone other than the author.
 - Locks can be removed by a user with the correct permission
 - Unlocking an item sends a notification to the author to which it was locked.
 - Manually unlocking a version does not lock it to the unlocking user, nor does it change the author.
 - The Version admin view for each content-type registered with Version-locking will be edited to add in lock icons / buttons UI to the Actions column.

Installation
------------
The package djangocms-versioning and djangocms-moderation need to be installed for this project to function correctly.


Configuration
-------------
Version-locking makes use of the django-cms 4.x App Registration mechanism to allow models from other addon's (i.e. content-types) to be registered for use with version-locking. 
`®`