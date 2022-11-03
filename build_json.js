const fs = require('fs');
const path = require('path');
const fm = require('front-matter');

const walk = function(dir, done) {
  var results = [];
  fs.readdir(dir, function(err, list) {
    if (err) return done(err);
    var pending = list.length;
    if (!pending) return done(null, results);
    list.forEach(function(file) {
      file = path.resolve(dir, file);
      fs.stat(file, function(err, stat) {
        if (stat && stat.isDirectory()) {
          walk(file, function(err, res) {
            results = results.concat(res);
            if (!--pending) done(null, results);
          });
        } else {
          results.push(file);
          if (!--pending) done(null, results);
        }
      });
    });
  });
};


const buildData = (posts) => posts
  .map(post => {
    const content = fs.readFileSync(post, 'utf8');
    const attributes = fm(content).attributes;
    const { title, date, status, subtitle, authors, excerpt } = attributes;
    
    if(!title) throw new Error('Missing title on '+post);
    if(!date) throw new Error('Missing date on '+post);
    
    const fileName = path.basename(post, '.md').split('.')[0];
    const lang = getLanguage(post);
    const translations = posts.filter(l => l.includes(fileName)).map((l) => { return getLanguage(l) }).filter(l => l !== lang);
    
    const slug = attributes.slug || path.basename(post, '.md');
    return {
        slug: slug.substring(slug.indexOf("]")+1), //removing status from file name, e.g: "[unassigned]hello.md" will be "hello.md"
        fileName: path.basename(post),
        status: status || 'published', authors: authors || null,
        title, date, lang, translations, subtitle, excerpt,
    };
});

const getLanguage = (post) => {
    const fileName = path.basename(post, '.md');
    if ((/.*\.[a-z]{2}/g).test(fileName)) 
        return fileName.split('.').pop();
    else
        return "us";
};

const createJSON =(content, fileName) => {
    if (!fs.existsSync("api")) fs.mkdirSync("api");
    fs.writeFileSync("api/"+fileName+".json", JSON.stringify(content, null, 2));
};

walk('blog/', function(err, results) {
    if (err){
        console.log("Error scanning markdown files");
        process.exit(1);
    } 
    
    try{
        const posts = buildData(results);
        createJSON(posts, "posts");
        console.log("The ./api/posts.json file was created!");
        process.exit(0);
    }
    catch(error){
        console.log(error);
        process.exit(1);
    }
});