#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;   // normalized coords UV (0, 1)
in vec4 fragColor;
in vec2 vertCoord;

uniform vec2 spriteSize;
uniform vec2 tilemapSize;
uniform vec2 tileSize;

// Input uniform values
uniform mat4 mvp;
uniform sampler2D texture0;
uniform sampler2D texture1;
uniform vec4 colDiffuse;

// Output fragment color
out vec4 finalColor;

void main()
{
    // Texel color fetching from texture sampler
    vec4 texelColor = texture(texture0, fragTexCoord);
    vec2 tileCoord = vertCoord / tileSize;
    vec2 texelCoord = tileCoord / tilemapSize;
    vec4 maskColor = texture(texture1, texelCoord);
    vec4 baseColor = texelColor * colDiffuse;

    finalColor = mix(baseColor, vec4(0.8, 0.2, 0.8, 0.1) * baseColor, 1 - maskColor.x);
}
