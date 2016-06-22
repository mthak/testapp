import groovy.json.JsonSlurper
def slurper = new JsonSlurper()

//def jobsJson = new JsonSlurper().parseText( new URL( 'https://api.github.com/repos/mthak/spark/git/trees/master?' ).text )
//println jobsJson
def giturl = "http://github.com/mthak/spark.git"
def branch = "master"
def command = "-e clean deploy -DskipTests"
def jobsJson = slurper.parseText(readFileFromWorkspace("new.json"))

jobsJson.projects.each { team,projects -> 
     jobnames=projects
     folder(team) {
         displayName(team)
             description('Folder for project')
             }

     println "created folder" + team
     jobnames.each { jobs,config ->
         println "Jobs name is " + jobs
         println "config for jobs is " + config
         mavenJob("${team}/${jobs}") {
            scm {
              git(config.giturl,config.branch)
            }
            triggers {
            }
             goals(config.buildscript)
   }
}
}
/*if (it.type == 'tree' && it.path != '.github') {
   path = it.path
   println "Creating jobs " + path
mavenJob("SPM-${it.path}") {
    scm {
        git(giturl,branch)
    }
    triggers {
    }
        rootPOM("${path}/pom.xml")
        goals(command)
    /*steps {
        maven(command)
    }
}
}
}*/
categorizedJobsView('SPM-Jobs') {
    jobs {
        regex(/SPM-.*/)
    }
    categorizationCriteria {
        regexGroupingRule(/^SPM-.*$/, namingRule="SPM-Master")

    }
    description("SPM-Master")
    columns {
        status()
        categorizedJob()
        buildButton()
    }
}
