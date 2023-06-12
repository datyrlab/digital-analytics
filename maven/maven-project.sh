#! /bin/bash

# tag::code[]

# how to this script works
# 1. creates a maven project directory
# 2. writes dependencies and plugins to your pom file
#       will look for any file with extension .xml
#       ensure the xml file contains no more than one item

# to run the script
# bash /your/path.../maven/project.sh "<mvn command to create a project>"


# tag::variables

if  [[ $1 ]]; then 
    
    project_dir=$(dirname $(dirname $(realpath $0 )))
    mavendirectory=`dirname $0`
    mavencommand="$1"
    pomitemdirectory="${mavendirectory}/${2}"  
    maven_assembly_plugin="${mavendirectory}/${pomitemdirectory}/pom-plugin-maven-assembly-plugin.xml"

    #projectdirectory="${mavendirectory}/projects-maven" # create projects dir inside the maven directory
    projectdirectory=$(echo ${mavendirectory%/*}"/projects-maven") # create projects dir outside the maven directory
    #projectdirectory="<or set a preferred location>"
    #projectdirectory=$(dirname $(dirname $(dirname $(realpath $0 )))) # same level as the script-bash directory

    projectname=$(echo $mavencommand | sed -r 's/.*DartifactId=([^ ]+).*/\1/')
    projectfolder="${projectdirectory}/${projectname}" # full path to your project
    projectpomfile="${projectdirectory}/${projectname}/pom.xml"
    
    #<mainClass> - we set this value in our maven-assembly-plugin
    mainclass=$(echo $mavencommand | sed -r 's/.*DgroupId=([^ ]+).*/\1/')
    mainclass="${mainclass}.App" # App is the default main class that is created
   
    # resource folders
    resourcesdirectory="${projectdirectory}/${projectname}/src/main/resources"
    #resourcesdirectory="${projectdirectory}/src/main/resources"
    
    # resource subdirectories - add more directories
    resource_subdirectories=(
        "/config"
    )

fi

# end::variables


# uncomment to delete your .m2 directory for a complete restart
# if [ -f ~/.m2 ]; then rm -rf ~/.m2i; fi


# tag::maven_project
function maven_project(){
    
    if  [[ $1 ]]; then MAVENCOMMAND=$1; fi    
    if  [[ $2 ]]; then PROJECTDIRECTORY=$2; fi    
    if  [[ $3 ]]; then PROJECTFOLDER=$3; fi    
    if  [[ $4 ]]; then RESOURCESDIRECTORY=$4; fi    
    if  [[ $5 ]]; then eval "declare -A RESOURCE_SUBDIRECTORIES="${5#*=}; fi

    # is maven installed
    verify=$(mvn -version)
    
    if [[ ! ${verify} =~ "Apache Maven" ]]; then
        echo -e "\nmaven is not installed\n"

    else
        if [ ! -d ${PROJECTDIRECTORY} ]; then
            mkdir ${PROJECTDIRECTORY}        
        fi

        # create project if directory doesn't exist
        if [ ! -d ${PROJECTFOLDER} ]; then
            cd ${PROJECTDIRECTORY}
            pwd # show current directory
            eval $MAVENCOMMAND

        else
            echo -e "\nproject already exists"

        fi  
         
        # resources directories
        if [ -d ${PROJECTFOLDER} ]; then

            if [ ! -d ${RESOURCESDIRECTORY} ]; then
                mkdir ${RESOURCESDIRECTORY}        
                echo -e "created resource directory: ${RESOURCESDIRECTORY}"
            fi
            
            if  [[ $RESOURCE_SUBDIRECTORIES ]]; then
                for sub in "${RESOURCE_SUBDIRECTORIES=[@]}"; do
                    if [ ! -d ${RESOURCESDIRECTORY}${sub} ]; then
                        mkdir -p ${RESOURCESDIRECTORY}${sub}        
                        echo -e "created resource subdirectory: ${RESOURCESDIRECTORY}${sub}"
                    fi
                done
            fi

        fi
        
    fi
    
    
}
# end::maven_project


# tag::maven_mainclass
function maven_mainclass(){
    
    if  [[ $1 ]]; then MAVEN_ASSEMBLY_PLUGIN=$1; fi    
    if  [[ $2 ]]; then MAINCLASS=$2; fi    
    
    if [ -f ${MAVEN_ASSEMBLY_PLUGIN} ]; then
        mainclassstr="<mainClass>$MAINCLASS<\/mainClass>"
        sed -i -r "s/<mainClass>.*?<\/mainClass>/$mainclassstr/g" ${MAVEN_ASSEMBLY_PLUGIN}
                        
    fi

}
# end::maven_mainclass


# tag::update_pom
function update_pom(){
    
    if  [[ $1 ]]; then POMITEMFILE=$1; fi    
    if  [[ $2 ]]; then PROJECTPOMFILE=$2; fi    
    
    # looks for xml comment in pom item file (url page of plugin or dependency)
    search=$(grep -P "<!--.*?-->" $POMITEMFILE)
    
    # open pom item 
    POMITEMCONTENT=$(cat ${POMITEMFILE})
    POMITEMCONTENT="${POMITEMCONTENT##*( )}"
    POMITEMCONTENT="${POMITEMCONTENT%%*( )}"
   
    if  [[ $search ]]; then    
    
        if grep -Fxq "$search" ${PROJECTPOMFILE} # search for pom item in destination pom file
        then
            echo -e "already added: $search"

        else
            POMITEMCONTENT="$POMITEMCONTENT"$'\n' # add a trailing line break to each item, comment out if prefered

            if [[ $POMITEMCONTENT =~ "<dependency>" ]]; then
                # add item after last match
                # awk causes issues with escaping strings so insert this string then replace it after
                full_string=$(awk 'NR == FNR {
                    if ($0 ~ /<\/dependency>/)
                        x=FNR+1
                        next
                }
                FNR == x {
                    printf "\nINSERT_NEW_DEPENDENCY_HERE"
                }1' $PROJECTPOMFILE $PROJECTPOMFILE)
                full_string="${full_string//INSERT_NEW_DEPENDENCY_HERE/$POMITEMCONTENT}"
             
            elif [[ $POMITEMCONTENT =~ "<plugin>" ]]; then
                full_string=$(awk 'NR == FNR {
                    if ($0 ~ /<\/plugin>/)
                        x=FNR+1
                        next
                }
                FNR == x {
                    printf "\nINSERT_NEW_PLUGIN_HERE"
                }1' $PROJECTPOMFILE $PROJECTPOMFILE)
                full_string="${full_string//INSERT_NEW_PLUGIN_HERE/$POMITEMCONTENT}"

            elif [[ $POMITEMCONTENT =~ "<resource>" ]]; then
                if ! grep -Fxq "<resources>" ${PROJECTPOMFILE}
                then
                    POMITEMCONTENT="<resources>"$'\n'"${POMITEMCONTENT}</resources>"$'\n\n'
                    
                    full_string=$(awk 'NR == FNR {
                        if ($0 ~ /<\/testSourceDirectory>/)
                            x=FNR+1
                            next
                    }
                    FNR == x {
                        printf "\nINSERT_NEW_RESOURCE_HERE"
                    }1' $PROJECTPOMFILE $PROJECTPOMFILE)
                
                else
                    
                    full_string=$(awk 'NR == FNR {
                        if ($0 ~ /<\/resource>/)
                            x=FNR+1
                            next
                    }
                    FNR == x {
                        printf "\nINSERT_NEW_RESOURCE_HERE"
                    }1' $PROJECTPOMFILE $PROJECTPOMFILE)
                
                fi
                
                full_string="${full_string//INSERT_NEW_RESOURCE_HERE/$POMITEMCONTENT}"
            
            fi
            
            echo "${full_string}" > $PROJECTPOMFILE
            echo -e "adding to pom file: ${search}" 
        
        fi
    
    else
        echo -e "no item found: $POMITEMFILE"
    
    fi

}
# end::update_pom


# tag::maven_pom
function maven_pom(){
    
    if  [[ $1 ]]; then POMITEMDIRECTORY=$1; fi    
    if  [[ $2 ]]; then PROJECTPOMFILE=$2; fi    
    
    if [ -f ${PROJECTPOMFILE} ]; then
        echo -e "------------------------------------------------"
        echo -e "your project pom file: ${PROJECTPOMFILE}"
        
        if [ -d ${POMITEMDIRECTORY} ]; then
            IGNORE="ignore-" # add regex here to ignore file names
            if [ "$(ls ${POMITEMDIRECTORY} -1 | grep -v ${IGNORE})" ]; then

                filelist=($(ls ${POMITEMDIRECTORY} -1 | grep -v ${IGNORE}))

                for file in "${filelist[@]}"; do 
                     
                    if [[ $file =~ ".xml" ]]; then
                        pomitemfile="${POMITEMDIRECTORY}/${file}"
                        update_pom "${pomitemfile}" "${PROJECTPOMFILE}"
                        
                    fi

                done

            fi

        fi
    
    else
        echo -e "pom file doesn't exist"

    fi

}
# end::maven_pom


# tag::execute

if  [[ $mavencommand ]]; then 
    echo "project directory: ${projectdirectory}"
    # create project
    maven_project "${mavencommand}" "${projectdirectory}" "${projectfolder}" "${resourcesdirectory}" "$(declare -p resource_subdirectories)"
    
    # update pom file
    maven_mainclass "${maven_assembly_plugin}" "${mainclass}" 
    maven_pom "${pomitemdirectory}" "${projectpomfile}" 

fi

# end::execute

# end::code[]
