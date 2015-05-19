#ifdef GL_ES
precision mediump float;
#endif
varying vec2 v_texcoord;
uniform sampler2D tex;
uniform float alpha;

void main() {
    //gl_FragColor = vec4(1.0,0,0,0.1);
    gl_FragColor = texture2D( tex, v_texcoord ) * vec4(alpha); 
}
