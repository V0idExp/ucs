#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;
in vec4 fragColor;
in vec2 vertCoord;

// Input uniform values
uniform sampler2D texture0;
uniform sampler2D texture1;
uniform vec4 colDiffuse;
uniform vec2 spriteSize;
uniform vec2 tilemapSize;
uniform vec2 tileSize;

// Output fragment color
out vec4 finalColor;

void main()
{
    // Lookup the texel color
    vec4 texelColor = texture(texture0, fragTexCoord);

    // Lookup the mask color
    vec2 tileCoord = vertCoord / tileSize;
    vec2 maskTexCoord = tileCoord / tilemapSize;
    vec4 maskColor = texture(texture1, maskTexCoord);

    // Compute the final color, which will be mixed with a translucenct shade
    // based on whether it is obscured by the mask
    vec4 baseColor = texelColor * colDiffuse;
    finalColor = mix(baseColor, vec4(0.8, 0.2, 0.8, 0.1) * baseColor, 1 - maskColor.x);
}
