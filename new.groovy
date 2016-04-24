import groovy.json.JsonSlurper
bsView('APM-Jobs') {
    jobs {
    }
    categorizationCriteria {
        regexGroupingRule(/^APM-.*$/)
    }
    columns {
        status()
        categorizedJob()
        buildButton()
    }
}
def slurper = new JsonSlurper()

def jobsJson = new JsonSlurper().parseText( new URL( 'https://api.github.com/repos/mthak/spark/git/trees/master?' ).text )
//println jobsJson
def giturl = "http://github.com/mthak/spark.git"
def branch = "master"
def command = "-e clean deploy -DskipTests"
jobsJson.tree.each { 
if (it.type == 'tree' && it.path != '.github') {
   path = it.path
   println "Creating jobs " + path
mavenJob("APM-${it.path}") {
    scm {
        git(giturl,branch)
    }
    triggers {
     scm('*/15 * * * *')
    }
        rootPOM("${path}/pom.xml")
        goals(command)
    /*steps {
        maven(command)
    }*/
}
}
}

categorizedJobsView('APM-Jobs') {
    jobs {
        regex(/APM-.*/)
    }
    categorizationCriteria {
        regexGroupingRule(/^APM-.*$/)
    }
    columns {
        status()
        categorizedJob()
        buildButton()
    }
}
