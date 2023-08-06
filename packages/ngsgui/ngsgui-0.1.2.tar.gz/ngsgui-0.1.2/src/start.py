#!/usr/bin/python3

# -*- coding: utf-8 -*-
import sys, os
import ngsgui as G
import ngsolve as ngs
import netgen.meshing


def main():
    
    def Draw(obj, *args, tab=None, **kwargs):
        """Draw a Mesh or a CoefficientFunction, this function is overridden by
        the new gui and returns the drawn scene."""
        scene = None
        for _type, creator in G.GUI.sceneCreators:
            if isinstance(obj,_type):
                scene = creator(obj, *args, **kwargs)
                break
        if scene:
            G.gui.draw(scene, tab=tab)
            return scene
        print("Cannot draw object of type ",type(obj))

    def Redraw(blocking=True,**kwargs):
        if blocking:
            G.gui.redraw_blocking()
        else:
            G.gui.redraw()
    ngs.Draw = Draw
    ngs.Redraw = Redraw
    G.gui = G.GUI()
    G.gui.parseFlags(sys.argv[1:])
    G.gui.run()

if __name__ == "__main__":
    main()
