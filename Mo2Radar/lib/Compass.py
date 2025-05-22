    def build_compass(self):
        """build compass direction indicators"""
        self.directions = []
        # cardinal directions
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = math.cos(rad) * Radar.RADIUS * 0.9
            y = math.sin(rad) * Radar.RADIUS * 0.9
            line = shapes.Line(
                x=Radar.CENTER[0],
                y=Radar.CENTER[1],
                x2=Radar.CENTER[0] + x,
                y2=Radar.CENTER[1] + y,
                color=(170, 170, 170, 170),
                batch=Radar.BATCH,
            )
            self.directions.append(line)
            
            # Add direction labels
            labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            label = pyglet.text.Label(
                labels[angle // 45],
                font_name="DejaVu Sans",
                font_size=10,
                x=Radar.CENTER[0] + x * 1.1,
                y=Radar.CENTER[1] + y * 1.1,
                anchor_x="center",
                anchor_y="center",
                color=(255, 255, 255, 170),
                batch=Radar.BATCH,
            )
            self.directions.append(label)