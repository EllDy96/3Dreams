
var createRepo = require( 'github-create-repo' ); 

var opts = {
    'token': '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'
};
 
createRepo( '3Dreamers', opts, clbk );
 
function clbk( error, repo, info ){
    // Check for rate limit information...
    if ( info ) {
                                 console.error( 'Limit: %d', info.limit );
        console.error( 'Remaining: %d', info.remaining );
        console.error( 'Reset: %s', (new Date( info.reset*1000 )).toISOString() );
    }
    if ( error ) {
        throw new Error( error.message );
    }
    console.log( JSON.stringify( repo ) );
    // returns <repo_data>
}
