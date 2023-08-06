def updatebuildnumber(name):
    print("##vso[build.updatebuildnumber]{}".format(name))
    print("Updated build number to {}".format(name))

    updatebuildname = updatebuildnumber