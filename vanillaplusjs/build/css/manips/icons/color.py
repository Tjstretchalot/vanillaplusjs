from dataclasses import dataclass


@dataclass
class Color:
    """Describes a color via the red, green, and blue values (0-255 each)"""

    red: int
    green: int
    blue: int

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Converts the given hex string to the color value. This supports
        two formats: #RRGGBB and #RGB. This is not intended to act as a
        validator that the hex_str does indeed represent a color.
        """
        if hex_str[0] != "#":
            raise ValueError("Hex string must start with #")

        if len(hex_str) == 7:
            return cls(
                red=int(hex_str[1:3], 16),
                green=int(hex_str[3:5], 16),
                blue=int(hex_str[5:7], 16),
            )

        if len(hex_str) == 4:
            return cls(
                red=int(hex_str[1] * 2, 16),
                green=int(hex_str[2] * 2, 16),
                blue=int(hex_str[3] * 2, 16),
            )

        raise ValueError("Hex string must be 7 or 4 characters long")

    def to_hex(self) -> str:
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"
