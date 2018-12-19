class getData extends Thread
{

  getData()
  {
    running=false;
  }

  void start()
  {
    running=true;
    println("Comienza toma de datos");
    super.start();
  }

  void run()
  {
    while (running)
    {
      if (myPort.available() > 0)
      {
        // If data is available,
        //println("llego dato");
        //leo el dato
        try 
        {
          //cVal = myPort.readBytesUntil('\n', Val);
          val = myPort.readStringUntil('\n').trim();
          //println("este es el string");
          //println(val);
        }
        catch (NullPointerException e) {
          //println("llego null");
        }
        //lo convierto en int
        try {
          iVal =Integer.parseInt(val);
          //println("este es el int");
          //println(iVal);
        }

        catch (NumberFormatException e) {
          //println("\"" + val + "\"");
          //println("can't be converted to a number!");
        }

        //Salvo el tiempo
        tiempo = System.currentTimeMillis()-tiempoInit;

        //diferencio el tipo de dato (ECG o PO)
        tDato = iVal & 0xF000;
        //println(tDato);
        vDato = iVal & 0x0FFF;
        //println(vDato);
        //el valor del dato (nro del 0 - 1023)
        //vDato = iVal & 0x0FFF;
        if (tDato == 0xA000)
        {
          //println("llego ECG");
          //tengo datos del ECG, guardo tiempo,dato
          fECG.println(tiempo+","+vDato);
          fECG.flush();
          //agrego el dato al plot
          pECG.add(tiempo, vDato);
        } else if (tDato == 0x5000)
        {
          //println("llego PO");
          //tengo datos del PO, guardo tiempo,dato
          fPO.println(tiempo+","+vDato);
          fPO.flush();
          //agrego el dato al plot
          pPO.add(tiempo, vDato);
        } else if (tDato == 0x7000)
        {
          println("revisar LOD+");
          //se desconecto LOD+
          
        } else if (tDato == 0x9000)
        {
          println("revisarLOD-");
          //se desconecto LOD-
          
        } else
        {
          //println("llego cualca");
        }
        try
        {
          Thread.sleep(2);
        }
        catch (InterruptedException e) {
          //me cabe
        }
      }
    }
  }

  void quit()
  {
    running=false;
    interrupt();
  }
}
