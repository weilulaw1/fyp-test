import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";

import plantumlEncoder from "plantuml-encoder";

const examples = {
  Sequence: `@startuml
Alice -> Bob : Hello
Bob --> Alice : Hi
@enduml`,

  UseCase: `@startuml
actor User
rectangle System {
  User --> (Login)
  User --> (Upload File)
}
@enduml`,

  Class: `@startuml
class User {
  +id: int
  +name: string
  +login()
}
class Admin
User <|-- Admin
@enduml`,

  Activity: `@startuml
start
:Login;
if (Valid?) then (yes)
  :Show Dashboard;
else (no)
  :Show Error;
endif
stop
@enduml`,
};

export default function PlantUMLSwiper() {
  return (
    <div style={{ width: "80%", margin: "0 auto" }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
        UML Diagrams
      </h2>
      <Swiper
        modules={[Pagination, Navigation]}
        pagination={{ clickable: true }}
        navigation
        spaceBetween={30}
        slidesPerView={1}
      >
        {Object.entries(examples).map(([name, uml]) => {
          const url = `http://localhost:8080/svg/${plantumlEncoder.encode(uml)}`;
          return (
            <SwiperSlide key={name}>
              <div style={{ textAlign: "center" }}>
                <h3>{name} Diagram</h3>
                <img
                  src={url}
                  alt={`${name} diagram`}
                  style={{ maxWidth: "100%", height: "auto" }}
                />
              </div>
            </SwiperSlide>
          );
        })}
      </Swiper>
    </div>
  );
}
