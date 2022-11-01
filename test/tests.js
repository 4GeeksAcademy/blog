const fs = require('fs');
const _path = require('path');
const fm = require('front-matter');
const moment = require('moment');
const colors = require('colors');
const { POSSIBLE_STATUS } = require("./variables")
const { walk, indexContent } = require('./file')


const TestError = (blogPost, message) => {
    return {
        message,
        type: "error",
        path: blogPost.path
    }
}


let slugs = [];
const validateLessons = (report) => {
    let warnings = [];
    const addWarning = (blogPost, message) => {
        warnings.push({
            message,
            path: blogPost.path
        });
    }
    report.blogPosts.forEach((l) => {
    
        if(!l){
            console.log("Skipping: ", l);
            return false;
        } 
        const { content, fileName, originalSlug, path } = l;
        
        const { slug, title, date, tags, status, authors, subtitle, ...rest } = fm(content).attributes;
        
        // if(fileName.indexOf('.es') > -1){
        //     if(!report.names.includes(originalSlug)){
        //         if(status!='draft') throw TestError(l,`Lesson must have an english version ${originalSlug}`);
        //         else throw TestError(l,`Lesson must have an english version ${originalSlug}`)
        //     } 
        // } 
        
        if(!title) throw TestError(l,'Missing blogPost title'.red);
        
        if(rest.cover && rest.cover.indexOf("../") > -1) throw TestError(l,'The cover attribute can only be used for remote images, if the image is local please use cover_local instead'.red);
        else if(rest.cover_local){
            if(rest.cover_local.indexOf("../") == -1) throw TestError(l,'The cover_local attribute can only be used for local images, if the image is remote please use cover instead'.red);
            const _p = "../"+rest.cover_local.replace("../../","");
            if(!fs.existsSync(_path.join(__dirname, _p))) throw TestError(l,`This image from cover_local could not be found: ${_p}`.red);
        }
        
        //if(!tags || !Array.isArray(tags) || tags.length == 0) throw TestError(l,`Lesson tags must be an array and have at least one tag`.red);
        if(authors && !Array.isArray(authors)) throw TestError(l,`Author property must be an array of strings (github usernames) of post authors`.red);
        if(status && !POSSIBLE_STATUS.includes(status)) throw TestError(l,`The blogPost status must be one of ${POSSIBLE_STATUS.join(',')} but it is ${status}. \n ${path}`.red);
        if(!moment(date).isValid()) throw TestError(`Invalid blogPost date: ${date}`.red);

        // if(status=='published' || !status){
        //     if(!subtitle || subtitle == '' || subtitle?.length < 50 || subtitle?.length > 340) throw TestError(l,`The blogPost must have a subtitle within 50 and 340 characters, ${subtitle?.length || 0} found`.red);
        // }
        if(slug && slugs.includes(slug)) throw TestError(l,`Duplicated blogPost slug: ${slug} in two or more blogPosts in: ${path}`.red);
        slugs.push(slug);
        
        return warnings;
    });
    return warnings;
}

walk('blog', function(err, results) {
    if (err){
        console.log("Error scanning blogPost files".red);
        process.exit(1);
    } 
    
    try{
        const warnings = validateLessons(indexContent(results));
        if(warnings.length == 0) console.log("Success!! All files are valid".green);
        else{
            console.log(`Warning!! Passed but with ${warnings.length} warnings`.yellow);
            warnings.forEach((w,i) => {
                console.log("");
                console.log(`${i}) ${w.message}`.yellow);
                console.log(w.path);
                console.log("");
                console.log("================================================================");
            })
            process.exit(0);
        } 
    }
    catch(error){
        console.log(error.message ? error.message.red : error);
        console.log(error.path ? error.path.red : "");
        process.exit(1);
    }
});